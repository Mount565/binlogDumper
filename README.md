# binlogDumper
Dump mysql binlog and decode them to plain sql and rollback sql IN REAL TIME!

This program depends on pymysqlreplication and tested on python 3.5!

Before running this script, it is advised to run flush logs on the master(of course depending on your use case.). So that the master start to write binlog events in a new file. This script by default dump all the binlog events in the current binlog file.

## How to use it

### Install Python3.5

wget -c https://www.python.org/ftp/python/3.5.4/Python-3.5.4.tgz

tar xzf Python-3.5.4.tgz

cd Python-3.5.4

./configure

make

make install

ln -s /usr/local/bin/python3.5 /usr/bin/python3 <br>
ln -s /usr/local/bin/pip3 /usr/bin/pip3
### Install mysql -replication
pip3 install mysql-replication
### Grant the following privileges to account test
GRANT REPLICATION SLAVE, REPLICATION CLIENT, SELECT ON \*.\* TO 'test'@'host'
### Run the program

python3  binlogParser.py --host=192.168.216.146 --port=3306 --user=test --password=test --serverId=1 <br>
or run it in background <br>
```
nohup python3  binlogParser.py --host=192.168.216.146 --port=3306 --user=test --password=test --serverId=1 &  

nohup python3 binlogParser.py --host=192.168.210.23--port=3306 --user=repl --password=repl --serverId=10 --onlyTables="table1","table2" --onlySchemas="db1","db2" &
```
Catch only specified binlog events
```
nohup python3 binlogDumper-master/binlogParser.py --host=17.0.1.17 --port=3306 --user=repl --password=repl --serverId=17 --onlyEvents=[QueryEvent,GtidEvent] --sqlDir=/mnt/resource/sql_logs &
```
You can also filter sqls for a specific GTID
```
python3 binlogDumper-master/binlogParser.py --host=17.0.1.17 --port=3306 --user=repl --password=repl --serverId=17  --sqlDir=/mnt/resource/sql_logs --gtid='b2d64755-2f09-11e7-8aeb-0017fa00d14d:23544245' --startFile='binlog.000296'
```

Note: --serverId is the master's server_id , you can get it by executing select @@global.server_id; on the master  
--sqlDir=/mnt/resource/sql_logs:  be sure you have **write permission** for this directory

### Filter out the sql statements you want  
./find_gtid.sh rollback_2018-07-26.sql d5902ad8-ec43-11e7-9df7-5254006b29ec:4567774
