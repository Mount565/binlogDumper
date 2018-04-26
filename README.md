# binlogDumper
Dump mysql binlog and decode them to plain sql and rollback sql

This program depends on pymysqlreplication!

Before running this script, it is advised to run flush logs on the master(of course depending on your use case.). So that the master start to write binlog events in a new file. This script by default dump all the binlog events in the current binlog file.

You can also specify the binlog and position to start to replicate with. In this case you need to change the following variables:

bin_log_file = 'stg-cs7-test-bin.000070'
start_position = 4

To filter tables and schemas, fill the following array variables:

only_tables = None

only_schemas = None
