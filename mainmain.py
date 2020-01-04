from datetime import datetime
import time
import os
# status_dir='status/'
# results=os.listdir(status_dir)
# status_fn=results[0]

log_file=open('main_log.txt','w+')
sleep_time_addon=30
current_sleep_time=5
threshold_for_sleep_increase=90
wait_upper_threshold=300
last_terminate_time=datetime.now()
while True:
    #current_start_id=os.listdir(status_dir)[0]
    os.system('python3 main.py')
    print('Program Exit. Taking a break...')
    log_file.write(str(datetime.now())+'#Program Terminated. Time elapsed: ' + \
                   str((last_terminate_time-datetime.now()).seconds)+'\n')
    if (last_terminate_time-datetime.now()).seconds <threshold_for_sleep_increase:
        current_sleep_time+=sleep_time_addon
        if current_sleep_time>wait_upper_threshold:
            #API may be blocked. Directly quit
            log_file.write(str(datetime.now())+'#Waittime Exceed Upper Threshold. Exit.\n')
    time.sleep(current_sleep_time)
    last_terminate_time=datetime.now()
