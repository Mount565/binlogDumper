#!/bin/bash

if [ $# -ne 2 ];then
  echo "Usage: sql file and an GTID arg are required. "
  echo "This program will print all the sql statement included in the GTID which is the arg you passed."
  echo "eg: $0 rollback_2018-07-26.sql d5902ad8-ec43-11e7-9df7-5254006b29ec:4567774"
  exit 1;
fi

file=$1
gtid=$2
cat $file | awk -v gtid=$gtid -F 'GTID:' '{if ($2==gtid) {n=1;print $0 } else if(n==1){print $0;n=0;}}'
