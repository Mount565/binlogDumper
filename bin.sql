# time: 2018-04-23T15:41:04 , binlog file:stg-cs7-test-bin.000071,binlog position:883,GTID:47c405d5-3b04-11e8-9c26-5254007205d6:914738
insert into test.t1 set age=10,id=6;
# time: 2018-04-23T15:41:56 , binlog file:stg-cs7-test-bin.000071,binlog position:1139,GTID:47c405d5-3b04-11e8-9c26-5254007205d6:914739
delete from test.t1 where age=99,id=5;
# time: 2018-04-23T15:43:19 , binlog file:stg-cs7-test-bin.000071,binlog position:1403,GTID:47c405d5-3b04-11e8-9c26-5254007205d6:914740
update test.t1 set age=90,id=6 where age=10,id=6;
# time: 2018-04-23T15:45:56 , binlog file:stg-cs7-test-bin.000071,binlog position:1843,GTID:47c405d5-3b04-11e8-9c26-5254007205d6:914742
insert into test.t2 set home='12',id=1;
# time: 2018-04-23T17:00:07 , binlog file:stg-cs7-test-bin.000071,binlog position:2104,GTID:47c405d5-3b04-11e8-9c26-5254007205d6:914743
insert into test.t2 set home='here',id=2;
# time: 2018-04-24T14:49:11 , binlog file:stg-cs7-test-bin.000071,binlog position:2365,GTID:47c405d5-3b04-11e8-9c26-5254007205d6:914744
insert into test.t2 set home='wang',id=3;
# time: 2018-04-24T14:49:56 , binlog file:stg-cs7-test-bin.000071,binlog position:2628,GTID:47c405d5-3b04-11e8-9c26-5254007205d6:914745
insert into test.t2 set home='longze',id=4;
# time: 2018-04-24T16:25:07 , binlog file:stg-cs7-test-bin.000071,binlog position:2891,GTID:47c405d5-3b04-11e8-9c26-5254007205d6:914746
insert into test.t2 set home='longze',id=4;
