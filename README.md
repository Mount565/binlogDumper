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
GRANT REPLICATION SLAVE, REPLICATION CLIENT, SELECT ON *.* TO 'test'@'host'
### Run the program
python3  binlogParser.py --host=192.168.216.146 --port=3306 --user=test --password=test --serverId=1 <br>
or run it in background <br>
nohup python3  binlogParser.py --host=192.168.216.146 --port=3306 --user=test --password=test --serverId=1 &
