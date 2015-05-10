import urllib2
import re
import pdb
import MySQLdb
import MySQLdb.cursors 
import sys
import os
import lib
import argparse
from datetime import datetime, date, time, timedelta

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--name', type=str, dest='name', action='store', help='event name')

args = parser.parse_args()
name = args.name
new_trucks = ""

if name == None:
    print "use --name to indicate the name of the event"
    sys.exit(-1)

log_file = open("/lamp/foodtrucksmap/foodtrucksmap/stuff/script/manual_input_event.log","aw")
old_stdout = sys.stdout

print "event: " + name

print "enter ? to giveup curent transaction"

date = "start"
skip = 0
total = 0
fail = 0
success = 0
sys.stdout = log_file
lib.start(name, "")
sys.stdout = old_stdout
while date != "/":
    date = raw_input("Enter date (yymmdd) (enter / to stop this event)")
    if date == "":
        date = raw_input('Can\'t be empty!!!! Enter date (yymmdd) (enter / to stop this event)')
    if date == "/":
        #sys.stdout = log_file
        lib.event_finish(name = name, url = "null", total=total, fail = fail, skip = skip, success = success, exit = False)
        #sys.stdout = old_stdout
        break
	
    if date == "?" :
        print "giving up this date and rerun"
	continue

    date = "20" + date[:2]+"-" + date[2:4] + "-" + date[4:]
    total += 1
    start_time = raw_input("Enter start time (hhmm like 1330 or 0900)")
    if start_time == "?":
        print "giving up this date and rerun"
	continue
    end_time = raw_input("Enter end time (hhmm like 1330 or 0900)")
    if end_time == "?":
        print "giving up this date and rerun"
	continue
    address = raw_input("Enter address (better to be formatted)")
    if address == "?":
        print "giving up this date and rerun"
	continue
    trucks = "";
    while True:
        truck_name = raw_input("Enter truck_name (do not have this \" in the name   and  enter '/' to stop)");
        if truck_name == "":
            truck_name = raw_input("Can\'t be empty!!!! Enter truck_name (do not have this \" in the name and enter '/' to stop)")
        if (truck_name == '/'):
            break

        if truck_name == "?":
            print "giving up all trucks and re-enter from begin"
	    trucks = "";
	    continue;


        # verify the trucks are known
	while True:
	    ret = lib.check_truck_name(truck_name)

	    if ret != True:
                new_truck_name = raw_input("not known truck name %s, input the corrected one, or enter ! to add this new truck: " % truck_name)

                if new_truck_name != "!":
	            truck_name = new_truck_name
                else:
	            new_trucks = new_trucks + "\""+ truck_name + "\" "
		    break
            else:
	        break

        truck_name = "\""+ truck_name+"\""; 
        trucks = trucks + truck_name + " ";


    #sys.stdout = log_file
    start_time = start_time[:2] + ":" + start_time[2:] + ":00"
    end_time = end_time[:2] + ":" + end_time[2:] + ":00"

    if start_time > "15:00:00":
        meal = "dinner" 
    else :
        meal = "lunch"


    ret_ok = lib.insert_event_into_database(name, date, meal, start_time, end_time, address, trucks)
     
    #sys.stdout = old_stdout
    if ret_ok == True:
        success += 1
    else :
        fail += 1
    
log_file.close()
lib.db.commit()
print log_file

if new_trucks != "":
    print "new trucks: " + new_trucks
