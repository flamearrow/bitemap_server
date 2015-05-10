import urllib2
import re
import pdb
import sys
import os
import lib
import getpass
from datetime import datetime, date, time, timedelta


default_file_name = getpass.getuser()+ datetime.now().strftime("_%Y_%M_%d_%H_%M_%S")
log_file_path = raw_input("Enter log file you wanti (default: ./logs/event_%s.log)" % default_file_name)
if (log_file_path == "") :
    log_file_path = "./logs/event_" + default_file_name + ".log"

if not os.path.exists(os.path.dirname(log_file_path)):
    os.makedirs(os.path.dirname(log_file_path))
log_file = open(log_file_path,"aw")
event_name = raw_input("Enter event_name (or skip)")
old_stdout = sys.stdout

total = 0
skip = 0
fail = 0
success = 0
while date != "/":
    name  = "none"
    while True:
        date = raw_input("Enter date (yymmdd) (enter / to stop this event")
	if date == "/":
	    break;
        input_date = date
        date = "20" + input_date[:2]+"-" + input_date[2:4] + "-" + input_date[4:]
        try: 
            datetime.strptime(date, '%Y-%m-%d')
        except: 
            print "ERROR: incorrect date " + input_date
            continue

        break
    if date == "/":
        break

    while True:
        while True:
            start_time = raw_input("Enter start time (hhmm like 1330 or 0900)")
            try: 
                datetime.strptime(start_time, '%H%M')
            except: 
                print "ERROR: incorrect start_time " + start_time
        	continue
            break
    
        while True:
            end_time = raw_input("Enter end time (hhmm like 1330 or 0900)")
            try: 
                datetime.strptime(end_time, '%H%M')
            except: 
                print "ERROR: incorrect end_time " + end_time
        	continue
            break
    
        if end_time <= start_time:
            print "ERROR: end_time %s is smaller than start_time %s" % (end_time,start_time)
    	    continue
        else:
            break
    address = raw_input("Enter address (better to be formatted)")
    sys.stdout = log_file
    lib.start(event_name, "")
    sys.stdout = old_stdout
    start_time = start_time[:2] + ":" + start_time[2:] + ":00"
    end_time = end_time[:2] + ":" + end_time[2:] + ":00"
    while name != "/":
        name = raw_input('Enter Truck name: (enter / to stop) ')
        if name == "/":
            break
	ret_name = []
	if lib.check_truck_name(name, ret_name) == False:
	    print "ERROR: Unknown truck name %s" % name
	    continue

        name = ret_name[0]
        total += 1

        sys.stdout = log_file

        if start_time > "15:00:00":
            meal = "dinner" 
        else :
            meal = "lunch"
    
        ret_ok = lib.insert_into_database(name, date, meal, start_time, end_time, address, event_name)
         
        sys.stdout = old_stdout
        if ret_ok == True:
            success += 1
        else :
            fail += 1

sys.stdout = log_file
lib.finish(name = event_name, url = "null", total=total, fail = fail, skip = skip, success = success, exit = False)
sys.stdout = old_stdout

log_file.close()
