from api_modules import Thingiverse
from pymongo import MongoClient
import requests
import random
import time
from datetime import datetime
import sys, os

status_dir='status/'
status_file_path=status_dir+os.listdir(status_dir)[0]
with open('key.txt', 'r') as k:
    auth_info=k.readlines()
    client_id=auth_info[0].strip('\n')
    client_secret=auth_info[1].strip('\n')
    token=auth_info[2].strip('\n')
print(client_id)
print(client_secret)
print(token)
t=Thingiverse({'client_id':client_id,'client_secret':client_secret})
t.connect(token)
client=MongoClient('localhost', 27017)
db=client.things
thing_info=db.thing_info
log_file=open('err_log.txt', 'a+')
log_file.write(str(datetime.now()) + '#Start\n')
range_from=int(os.listdir(status_dir)[0])
range_to=4000000
rest_threshold=50
rest_count=0
#Create folder to store files
dir_name='zip'+str(range_from)
if not os.path.exists(dir_name):
    os.makedirs(dir_name)
#File Count
fcount=0
fthreshold=10000
for tid in range(range_from, range_to):
    os.rename(status_file_path, status_dir + str(tid))
    #if rest_count >= rest_threshold:
        #print('\rReached Rest Threshold: taking a rest...')
        #del t
        #rest_count=0
        #time.sleep(random.uniform(60,90))
        #t=Thingiverse({'client_id':client_id,'client_secret':client_secret})
        #t.connect(token)
        #print('\rContinue                                ')
    #else:
        #rest_count+=1
    thing=t.get_thing(tid)
    if 'error' in thing:
        log_file.write(str(datetime.now()) +'#' + str(tid) + ':GetThingErr:' + thing['error'] + '\n')
        print("\r" + str(tid) + "Failed", end="", flush=True)
    else:
        thing_info.insert_one(t.get_thing(2))

        #Download thing zip
        s='/things/' + str(tid) + '/package-url'
        result=t._get_it(s,None)
        if result is None or result is {} or 'error' in result:
            log_file.write(str(datetime.now()) +'#' + str(tid) + ':DownloadErr:' + str(result) + '\n')
            print("\r" + str(tid) + "Download Failed", end="", flush=True)
        else:
            zip_link=result['public_url']
            r = requests.get(zip_link)
            zip_fname=dir_name+'/' + str(tid) + '.zip'
            with open(zip_fname, 'wb+') as f:
                f.write(r.content)
            print("\r" + str(tid) + "Downloaded", end="", flush=True)
            if fcount>fthreshold:
                dir_name='zip'+str(tid)
                if not os.path.exists(dir_name):
                    os.makedirs(dir_name)
                fcount=0
            else:
                fcount+=1
    #time.sleep(random.uniform(3,7))
    time.sleep(random.uniform(1,2))
    status_file_path=status_dir+str(tid)

        
