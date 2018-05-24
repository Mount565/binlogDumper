# binlogDumper
Dump mysql binlog and decode them to plain sql and rollback sql

This program depends on pymysqlreplication and tested on python 3.5!

Before running this script, it is advised to run flush logs on the master(of course depending on your use case.). So that the master start to write binlog events in a new file. This script by default dump all the binlog events in the current binlog file.

How to use it

eg: binlogParser.py --host=192.168.216.146 --port=3306 --user=test --password=test --serverId=1
