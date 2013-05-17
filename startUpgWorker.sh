#!/bin/bash

/usr/bin/killall  -9 python
cd /usr/apps/zayh/RemoteBox
/usr/bin/python  UpgWorker.py &  1> /dev/null
