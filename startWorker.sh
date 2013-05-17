#!/bin/bash

/usr/bin/killall  -9 python
cd /usr/apps/zayh/RemoteBox
bash shutdown.sh
/usr/bin/python  Worker.py &  1> /dev/null
