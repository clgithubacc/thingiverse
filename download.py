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
#print(client_id)
#print(client_secret)
#print(token)
t=Thingiverse({'client_id':client_id,'client_secret':client_secret})
t.connect(token)

# Load last status
status_dir='status/'
status_file_path=status_dir+os.listdir(status_dir)[0]

# Connect to Mongodb
client=MongoClient('localhost', 27017)
db=client.things
thing_info=db.thing_info
log_file=open('err_log.txt', 'a+')
log_file.write(str(datetime.now()) + '#Start\n')
range_from=int(os.listdir(status_dir)[0])
range_to=4000000
rest_threshold=50
rest_count=0

# Create folder to store files
img_dir_name='images/'
zip_dir_name='zips/'
dir_name='zip'+str(range_from)+'/'
if not os.path.exists(dir_name):
    os.makedirs(dir_name)
    os.makedirs(dir_name+img_dir_name)
    os.makedirs(dir_name+zip_dir_name)

# Define number of zip files per folder
fcount=0
fthreshold=1000

for tid in range(range_from, range_to):
    stid=str(tid)
    os.rename(status_file_path, status_dir + stid)
    try_count=3
    api_succeed=False
    thing=None
    while not api_succeed and try_count>0:
        api_succeed=True
        try:
            thing=t.get_thing(tid)
            if 'error' in thing:
                log_file.write(str(datetime.now()) + '#' + stid + ':GetThingErr:' + thing['error'] + '\n')
                print("\r" + stid + "Failed", end="", flush=True)
                continue
            thing_categories=t.get_thing_category(tid)
            thing['thing_categories_raw']=thing_categories
            thing_tags=t.get_thing_tags(tid)
            thing['thing_tags_raw']=thing_tags
            s = "/things/%d/images/" % (tid)
            thing_images = t._get_it(s, None)
            thing['thing_images_raw'] = thing_images
            s = "/things/%d/copies" % (tid)
            thing_makes = t._get_it(s, None)
            thing['thing_makes_raw']=thing_makes
            s = '/things/' + stid + '/package-url'
            thing_zip = t._get_it(s, None)
            thing['thing_zip_raw'] = thing_makes
        except:
            print("\r" + stid + "Failed.#", end="", flush=True)
            api_succeed=False
            time.sleep(1)
            try_count-=1
    if try_count<=0:
        sys.exit("Reached Max Try for thing# "+str(tid)+", Download Program Exits.")

    #Simple Preprocessing
    categories=[]
    for item in thing['thing_categories_raw']:
        categories.append(item['name'])
    thing['thing_categories']=categories
    tags = []
    for item in thing['thing_tags_raw']:
        tags.append(item['name'])
    thing['thing_tags'] = tags
    thing['thing_makes_count']=len(thing['thing_makes_raw'])

    # Download Images
    os.makedirs(dir_name+img_dir_name+stid+'/')
    for item in thing['thing_images_raw']:
        image_name=item['name']
        for img_type in item['sizes']:
            if img_type['type']=='display' and img_type['size']=='large':
                image_url=img_type['url']
                image_file = requests.get(image_url)
                image_fname = dir_name + img_dir_name + stid + image_name
                # Later thing images end w/ .stl are actually pngs
                if image_url.endswith('stl') or image_url.endswith('STL'):
                    image_fname+='.png'
                with open(image_fname, 'wb+') as f:
                    f.write(image_file.content)

    # Download Thing Zip
    zip_link = thing['thing_zip_raw']['public_url']
    zip_file = requests.get(zip_link)
    zip_fname = dir_name + zip_dir_name + stid + '.zip'
    with open(zip_fname, 'wb+') as f:
        f.write(zip_file.content)
    print("\r" + stid + "Downloaded", end="", flush=True)
    if fcount > fthreshold:
        dir_name = 'zip' + stid
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        fcount = 0
    else:
        fcount += 1

    time.sleep(random.uniform(1,2))
    status_file_path=status_dir+stid
