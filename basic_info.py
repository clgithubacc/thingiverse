from api_modules import Thingiverse
from pymongo import MongoClient
import requests
import random
import time
from datetime import datetime
import sys, os

# Connect to Thingiverse
with open('key.txt', 'r') as k:
    auth_info=k.readlines()
    client_id=auth_info[0].strip('\n')
    client_secret=auth_info[1].strip('\n')
    token=auth_info[2].strip('\n')

t=Thingiverse({'client_id':client_id,'client_secret':client_secret})
t.connect(token)

# Load last status
status_dir='status/'
status_file_path=status_dir+os.listdir(status_dir)[0]

# Connect to Mongodb
client=MongoClient('localhost', 27017)
db=client.things
thing_database=db.thing_simple


log_file=open('err_log.txt', 'a+')
log_file.write(str(datetime.now()) + '#Start\n')
inaccessible_file=open('inaccessible.txt', 'a+')
range_from=int(os.listdir(status_dir)[0])
range_to=4360000
rest_threshold=50
rest_count=0
consecutive_fail_count=0
for tid in range(range_from, range_to):
    stid=str(tid)
    #os.rename(status_file_path, status_dir + stid)
    os.rename(status_file_path, status_dir + str(tid))
    is_ok=False
    tries_left=10
    while not is_ok and tries_left>0:
        try:
            thing=t.get_thing(tid)
            is_ok=True
        except:
            is_ok=False
            tries_left-=1
        time.sleep((10-tries_left)*0.5)
    if tries_left==0:
        inaccessible_file.write(stid+',')
        consecutive_fail_count+=1
        if consecutive_fail_count>5:
            exit()
        continue
    else:
        consecutive_fail_count=0
    if 'error' not in thing and thing is not None and thing is not []:
        thing_database.insert_one(thing)
    else:
        log_file.write(str(datetime.now()) + '#' + stid + ':GetThingErr:' + thing['error'] + '\n')
        print("\r" + str(datetime.now()) + 'Thing ' + stid + " Does Not Exist.#", end="", flush=True)
