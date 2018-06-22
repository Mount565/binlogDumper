#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pymysqlreplication as pm
import datetime
import threading, time
import sys, getopt, os
from pymysqlreplication.event import BinLogEvent, GtidEvent, QueryEvent, BeginLoadQueryEvent, ExecuteLoadQueryEvent
from pymysqlreplication.row_event import UpdateRowsEvent, WriteRowsEvent, DeleteRowsEvent


# Before running this script, it is advised to run flush logs on the master. So that the master
# start to write binlog events in a new file.
# This script by default dump all the binlog events in the current binlog file.

class BinlogDump(object):
    def __init__(self, connectionStr, serverId, sqlDir=None, startFile=None, startPos=None, onlyTables=None,
                 onlySchemas=None):

        today = datetime.datetime.now().strftime("%Y-%m-%d")

        # The privileges needed for the user
        # GRANT REPLICATION SLAVE, REPLICATION CLIENT, SELECT ON *.* TO 'test'@'host'
        # Change the host and user credential to fit your database
        # mysql_strings = {'host': '192.168.216.146', 'port': 3306, 'user': 'test', 'passwd': 'test'}
        self.connect_strings = connectionStr
        self.only_events = [GtidEvent, UpdateRowsEvent, WriteRowsEvent, DeleteRowsEvent, QueryEvent,
                            BeginLoadQueryEvent,
                            ExecuteLoadQueryEvent]

        self.only_tables = onlyTables

        self.only_schemas = onlySchemas

        # The binlog file and position to start to replicate with
        # You may need to change these two variables
        self.bin_log_file = startFile
        self.start_position = startPos
        self.server_id = serverId

        # create directory to store sql files generated
        if not sqlDir:
            sqlDir = sys.path[0]
        else:
            sqlDir = sqlDir.strip()
            # sqlDir=sqlDir.rstrip('/')

            if not os.path.exists(sqlDir):
                os.mkdir(sqlDir)

        self.sqlDir = sqlDir
        # the file holds rollback sql(DML)
        self.rollback_sql = os.path.join(self.sqlDir, "rollback_%s.sql" % today)

        # the file holds sql executed
        self.bin_sql = os.path.join(self.sqlDir, "bin_%s.sql" % today)

    def date_type_to_str(self, val):
        if isinstance(val, int) or isinstance(val, float):
            return str(val)
        else:
            return "'" + str(val) + "'"

    def form_update_sql(self, schema, table, vals_before, vals_after, is_rollback=False):
        sql = "update " + schema + "." + table + " set "
        tmp_set = ""
        tmp_where = ""
        for key in vals_before:
            tmp_set = tmp_set + key + '=' + self.date_type_to_str(vals_after[key]) + ','
            tmp_where = tmp_where + key + '=' + self.date_type_to_str(vals_before[key]) + ','

        if is_rollback:
            sql = sql + tmp_where.strip(',') + ' where ' + tmp_set.strip(',') + ";"
        else:
            sql = sql + tmp_set.strip(',') + ' where ' + tmp_where.strip(",") + ";"

        return sql

    def form_delete_sql(self, schema, table, vals, is_rollback=False):
        sql = "delete from " + schema + "." + table + " where "
        rollback = "insert into " + schema + "." + table + " set "
        tmp_cols = ""

        for key in vals:
            tmp_cols = tmp_cols + key + "=" + self.date_type_to_str(vals[key]) + ","

        if is_rollback:
            sql = rollback + tmp_cols.strip(',') + ";"
        else:
            sql = sql + tmp_cols.strip(',') + ";"

        return sql

    def form_insert_sql(self, schema, table, vals, is_rollback=False):
        sql = "insert into " + schema + "." + table + " set "
        rollback = "delete from " + schema + "." + table + " where "
        tmp = ""
        for key in vals:
            tmp = tmp + key + "=" + self.date_type_to_str(vals[key]) + ","
        if is_rollback:
            sql = rollback + tmp.strip(",") + ";"
        else:
            sql = sql + tmp.strip(",") + ";"
        return sql

    def append_sql_to_file(self, file, sql):
        with open(file, 'a', encoding='utf-8') as f:
            f.writelines(sql)

    def rotate_sqlfile(self):
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        # the file holds rollback sql(DML)
        self.rollback_sql = os.path.join(self.sqlDir, "rollback_%s.sql" % today)

        # the file holds sql executed
        self.bin_sql = os.path.join(self.sqlDir, "bin_%s.sql" % today)


    def process_stream(self):

        stream = pm.BinLogStreamReader(connection_settings=self.connect_strings, resume_stream=False,
                                       server_id=self.server_id, blocking=True,
                                       log_file=self.bin_log_file,
                                       log_pos=self.start_position,
                                       only_schemas=self.only_schemas, only_tables=self.only_tables,
                                       only_events=self.only_events)

        print("##connected to master... ")

        for binlogevent in stream:

            if isinstance(binlogevent, GtidEvent):
                gtid = binlogevent.gtid

            elif isinstance(binlogevent, QueryEvent):
                pass
            else:
                info = "# time: %s , binlog file:%s,binlog position:%s,GTID:%s" % (
                    datetime.datetime.fromtimestamp(binlogevent.timestamp)
                        .isoformat(), stream.log_file, stream.log_pos, gtid)
                schema = "%s" % binlogevent.schema
                table = "%s" % binlogevent.table
                for row in binlogevent.rows:
                    if isinstance(binlogevent, DeleteRowsEvent):
                        vals = row["values"]
                        rollback = self.form_delete_sql(schema, table, vals, True)
                        sql = self.form_delete_sql(schema, table, vals)
                    elif isinstance(binlogevent, UpdateRowsEvent):
                        vals = dict()
                        vals["before"] = row["before_values"]
                        vals["after"] = row["after_values"]
                        rollback = self.form_update_sql(schema, table, vals["before"], vals["after"], True)
                        sql = self.form_update_sql(schema, table, vals["before"], vals["after"])
                    elif isinstance(binlogevent, WriteRowsEvent):
                        vals = row["values"]
                        rollback = self.form_insert_sql(schema, table, vals, True)
                        sql = self.form_insert_sql(schema, table, vals)

                    self.append_sql_to_file(self.rollback_sql, info + "\n")
                    self.append_sql_to_file(self.rollback_sql, rollback + "\r\n")

                    self.append_sql_to_file(self.bin_sql, info + "\n")
                    self.append_sql_to_file(self.bin_sql, sql + "\r\n")

        stream.close()

        print("Exited!")


'''
command line args
--help 

--host
--port
--user
--password
--serverId

--sqlDir
--startFile
--startPos
--onlyTables=["t1","t2"]
--onlySchemas=["schema1","schema2"]

'''


def get_arg_value(arglist, arg):
    try:
        opts, args = getopt.getopt(args=arglist, shortopts=None,
                                   longopts=["help", "host=", "port=", "user=", "password=", "sqlDir=", "serverId=",
                                             "startFile=", "startPos=", "onlyTables=", "onlySchemas="])

        for k, v in opts:
            if k == arg:
                return v

    except getopt.GetoptError:

        print("arg parse error.")
        sys.exit(1)


def usage():
    print("Usage:")
    print("binlogParser.py ")
    print("    --host        # master host ip [necessary]")
    print("    --port        # master host port [necessary]")
    print("    --user        # the user to connect to master [necessary]")
    print("    --password    # password of the user [necessary]")
    print("    --serverId    # the server_id of the master [necessary]")
    print(
        "    --sqlDir      # the directory to store the generated sql file and rollback sql file,default same directory as this program")
    print("    --startFile   # the binlog file to start ")
    print("    --startPos    # the position of the file to start to dump")
    print("    --onlyTables  # only dump sqls that change these tables")
    print("    --onlySchemas # only dump sqls that executed on these schemas")

# start a thread to rotate output sql file everyday
def rotate_thread(d):
    while True:
        current_time = time.localtime(time.time())
        if current_time.tm_hour == 0 and current_time.tm_min == 0 and current_time.tm_sec == 0:
            d.rotate_sqlfile()
            print("Output sql file rotated.")
        time.sleep(1)
        #print("rotate thread wake up.")


if __name__ == '__main__':
    argv = sys.argv[1:]

    if len(argv) <= 4:
        usage()
        sys.exit(1)

    con_string = {'host': get_arg_value(argv, "--host"), 'port': int(get_arg_value(argv, "--port")),
                  'user': get_arg_value(argv, "--user"), 'passwd': get_arg_value(argv, "--password")}

    dumper = BinlogDump(connectionStr=con_string, sqlDir=get_arg_value(argv, "--sqlDir"),
                        serverId=int(get_arg_value(argv, "--serverId")), startFile=get_arg_value(argv, "--startFile"),
                        startPos=get_arg_value(argv, "--startPos"), onlySchemas=get_arg_value(argv, "--onlySchemas"),
                        onlyTables=get_arg_value(argv, "--onlyTables"))
    t = threading.Thread(target=rotate_thread, name="rotate_thread",args=(dumper,))
    t.start()


    dumper.process_stream()
