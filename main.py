from api_modules import Thingiverse
from pymongo import MongoClient
import requests
import random
import time

with open('key.txt','r') as k:
    auth_info=k.readlines()
    client_id=auth_info[0]
    client_secret=auth_info[1]
    token=auth_info[2]
t=Thingiverse({'client_id':client_id,'client_secret':client_secret})
t.connect(token)
client=MongoClient('localhost',27017)
db=client.things
thing_info=db.thing_info
log_file=open('err_log.txt','w+')

range_from=2
range_to=3978949
for id in range(range_from,range_to):
    thing=t.get_thing(id)
    if 'error' in thing:
        log_file.write(id+':GetThingErr:'+thing['error'])
    else:
        thing_info.insert_one(t.get_thing(2))

        #Download thing zip
        s='/things/'+str(id)+'/package-url'
        result=t._get_it(s,None)
        if 'error' in result:
            log_file.write(id+':DownloadErr:'+thing['error'])

        zip_link=result['public_url']
        r = requests.get(zip_link)
        with open('/zips/'+id+'.zip', 'wb+') as f:
            f.write(r.content)
    time.sleep(random.uniform(0,5))