# binlogDumper
Dump mysql binlog and decode them to plain sql and rollback sql

Before running this script, it is advised to run flush logs on the master. So that the master start to write binlog events in a new file. This script dump all the binlog events in the current binlog file.
