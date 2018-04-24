import pymysqlreplication as pm
import datetime
from pymysqlreplication.event import BinLogEvent, GtidEvent, QueryEvent, BeginLoadQueryEvent, ExecuteLoadQueryEvent
from pymysqlreplication.row_event import UpdateRowsEvent, WriteRowsEvent, DeleteRowsEvent

# Before running this script, it is advised to run flush logs on the master. So that the master
# start to write binlog events in a new file. This script dump all the binlog events in the current binlog file.

# the file holds rollback sql(DML)
rollback_sql = "rollback.sql"

# the file holds sql executed
bin_sql = "bin.sql"

# The privileges needed for the user
# GRANT REPLICATION SLAVE, REPLICATION CLIENT, SELECT ON *.* TO 'test'@'host'

mysql_strings = {'host': '192.168.216.146', 'port': 3306, 'user': 'test', 'passwd': 'test'}

only_events = [GtidEvent, UpdateRowsEvent, WriteRowsEvent, DeleteRowsEvent, QueryEvent, BeginLoadQueryEvent,
               ExecuteLoadQueryEvent]

stream = pm.BinLogStreamReader(connection_settings=mysql_strings, server_id=12, blocking=True, only_events=only_events)

print("connected to master... ")


def date_type_to_str(val):
    if isinstance(val, int) or isinstance(val, float):
        return str(val)
    else:
        return "'" + str(val) + "'"


def form_update_sql(schema, table, vals_before, vals_after, is_rollback=False):
    sql = "update " + schema + "." + table + " set "
    tmp_set = ""
    tmp_where = ""
    for key in vals_before:
        tmp_set = tmp_set + key + '=' + date_type_to_str(vals_after[key]) + ','
        tmp_where = tmp_where + key + '=' + date_type_to_str(vals_before[key]) + ','

    if is_rollback:
        sql = sql + tmp_where.strip(',') + ' where ' + tmp_set.strip(',') + ";"
    else:
        sql = sql + tmp_set.strip(',') + ' where ' + tmp_where.strip(",") + ";"

    return sql


def form_delete_sql(schema, table, vals, is_rollback=False):
    sql = "delete from " + schema + "." + table + " where "
    rollback = "insert into " + schema + "." + table + " set "
    tmp_cols = ""

    for key in vals:
        tmp_cols = tmp_cols + key + "=" + date_type_to_str(vals[key]) + ","

    if is_rollback:
        sql = rollback + tmp_cols.strip(',') + ";"
    else:
        sql = sql + tmp_cols.strip(',') + ";"

    return sql


def form_insert_sql(schema, table, vals, is_rollback=False):
    sql = "insert into " + schema + "." + table + " set "
    rollback = "delete from " + schema + "." + table + " where "
    tmp = ""
    for key in vals:
        tmp = tmp + key + "=" + date_type_to_str(vals[key]) + ","
    if is_rollback:
        sql = rollback + tmp.strip(",") + ";"
    else:
        sql = sql + tmp.strip(",") + ";"
    return sql


def append_sql_to_file(file, sql):
    with open(file, 'a', encoding='utf-8') as f:
        f.writelines(sql)


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
                rollback = form_delete_sql(schema, table, vals, True)
                sql = form_delete_sql(schema, table, vals)
            elif isinstance(binlogevent, UpdateRowsEvent):
                vals = dict()
                vals["before"] = row["before_values"]
                vals["after"] = row["after_values"]
                rollback = form_update_sql(schema, table, vals["before"], vals["after"], True)
                sql = form_update_sql(schema, table, vals["before"], vals["after"])
            elif isinstance(binlogevent, WriteRowsEvent):
                vals = row["values"]
                rollback = form_insert_sql(schema, table, vals, True)
                sql = form_insert_sql(schema, table, vals)

            append_sql_to_file(rollback_sql, info + "\n")
            append_sql_to_file(rollback_sql, rollback + "\r\n")

            append_sql_to_file(bin_sql, info + "\n")
            append_sql_to_file(bin_sql, sql + "\r\n")

stream.close()

print("Exited!")
