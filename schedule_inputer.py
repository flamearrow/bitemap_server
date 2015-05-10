import urllib2
import re
import pdb
import sys
import os
import lib
import getpass
from datetime import datetime, date, time, timedelta


name  = "none"
default_file_name = getpass.getuser()+ datetime.now().strftime("_%Y_%M_%d_%H_%M_%S")
log_file_path = raw_input("Enter log file you wanti (default: ./logs/schedule_%s.log)" % default_file_name)
if (log_file_path == "") :
    log_file_path = "./logs/schedule_" + default_file_name + ".log"

if not os.path.exists(os.path.dirname(log_file_path)):
    os.makedirs(os.path.dirname(log_file_path))
log_file = open(log_file_path,"aw")
old_stdout = sys.stdout

while name != "/":
    date = "start"
    name = raw_input('Enter Truck name: (enter / to stop) ')
    if name == "/":
        break
    ret_name = []
    if lib.check_truck_name(name, ret_name) == False:
        print "ERROR: Unknown truck name %s" % name
        continue

    name =ret_name[0]
    skip = 0
    total = 0
    fail = 0
    success = 0
    sys.stdout = log_file
    lib.start(name, "")
    sys.stdout = old_stdout
    while date != "/":
        while True:
            date = raw_input("Enter date (yymmdd) (enter / to stop this truck)")
            if date == "/":
                sys.stdout = log_file
                lib.finish(name = name, url = "null", total=total, fail = fail, skip = skip, success = success, exit = False)
                sys.stdout = old_stdout
                break

            input_date = date
            date = "20" + date[:2]+"-" + date[2:4] + "-" + date[4:]
	    try: 
	        datetime.strptime(date, '%Y-%m-%d')
	    except: 
	        print "ERROR: incorrect date " + input_date
		continue

            break

        if date == "/":
	    break
        total += 1
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
        event_name = raw_input("Enter event_name (or skip)")

        
        if any(skip_event in event_name.lower() for skip_event in lib.skip_events) or any(skip_event in address.lower() for skip_event in lib.skip_events):
            print "----skip----"
            print event_name + " " + address + date
            skip = skip + 1
            continue

        
        sys.stdout = log_file
        start_time = start_time[:2] + ":" + start_time[2:] + ":00"
        end_time = end_time[:2] + ":" + end_time[2:] + ":00"

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
        

log_file.close()
