from collections import OrderedDict
import sys
import pdb
import urllib2
import re
from datetime import datetime, date, time, timedelta
import time

import MySQLdb
import MySQLdb.cursors 

db = MySQLdb.connect(host="localhost",user="ft",passwd="",db="foodtrucks", cursorclass=MySQLdb.cursors.DictCursor, sql_mode="STRICT_ALL_TABLES")
db.autocommit(True)

c = db.cursor()

def event_finish(name, url, total=0, fail=0, skip=0, success = 0, exit = True):
    if fail != 0 or total == 0:
        failed = "FAILED"
    else:
        failed = ""

    if int(fail) + int(skip) + int(success) != int(total) :
        failed = "FAILED MATH_ERROR"

    print "------------DONE: name: %s url: %s  total: %s success: %s skip:%s fail: %s %s-------------------" % (name, url,total, success, skip, fail, failed)
   
    if exit == True:
        if failed == "":
            sys.exit(0)
        else:
            sys.exit(88)
def finish(name, url, total=0, fail=0, skip=0, success = 0, exit = True):
    if fail != 0 or total == 0:
        failed = "FAILED"
    else:
        failed = ""

    if int(fail) + int(skip) + int(success) != int(total) :
        failed = "FAILED MATH_ERROR"

    print "------------DONE: name: %s url: %s  total: %s success: %s skip:%s fail: %s %s-------------------" % (name, url,total, success, skip, fail, failed)
   
    if exit == True:
        if failed == "":
            sys.exit(0)
        else:
            sys.exit(88)

def start(name, url):
    print "------------START: name %s  url %s----------------" % (name, url)

def print_error(err_str):
    print "!!!ERROR: " + err_str + "!!!ERROR!!!"

def get_url_content(url):
    try:response = urllib2.urlopen(url, timeout=60)
    except Exception, e:
        print_error("fail to open the url")
        print e
        return ""

    return response.read()

def request_address_info(address):

    res_address_info = {'formatted_address': None, 'location': {'lat': None, 'lng': None}}
    GEOCODE_BASE_URL = 'https://maps.googleapis.com/maps/api/geocode/json'
    RESTRICTION = '&components=administrative_area:CA|country:US'
    KEY = 'AIzaSyAv11A9OptZ5TX-Pqr3egpbddHQzQ_yULU'
    encode_string = "address=" + re.sub(r'\W', '+', address) 
    url = GEOCODE_BASE_URL + '?' + encode_string + RESTRICTION + '&key=' + KEY
    result = simplejson.load(urllib2.urlopen(url))

    attempt = 0
    while result['status'] != 'OK' and attempt < 3:
        result = simplejson.load(urllib2.urlopen(url))
        attempt += 1
        if result['status'] == 'OVER_QUERY_LIMIT':
            time.sleep(1)   
            continue
        
    if result['status'] == 'OK':
        res_address_info['formatted_address'] = result['results'][0]['formatted_address']
        res_address_info['location']['lat'] = format(result['results'][0]['geometry']['location']['lat'])
        res_address_info['location']['lng'] = format(result['results'][0]['geometry']['location']['lng'])
        return res_address_info
    else:
        print_error("unexpected formatted address %s" % result)
        return res_address_info
        

def truck_name_to_id(name): 
    select_sql_fmt = """SELECT id FROM `all_trucks` where `name` = %s"""

    select_sql_args = (name)
    try : 
        c.execute(select_sql_fmt, select_sql_args)

	truck_id = c.fetchone()
        
	if truck_id == None:
	    return -1

	return int(truck_id['id'])

    except:
        print_error("sql fail")
	print "e: %s" %e

        return -1;


def get_sql_args(name, date, meal, start_time, end_time, address, lat = None, lng = None):
    if not lat:
        address_info = request_address_info(address)
    else:
        address_info = OrderedDict()
        address_info['formatted_address'] = address
        address_info['location']['lat'] = lat
        address_info['location']['lng'] = lng
    truck_id = truck_name_to_id(name);

    if truck_id <= 0:
        raise Exception("Unkown truck name : %s id :%s " % (name, truck_id))

    sql_args = (name, truck_id, date, meal, start_time, end_time, 
                address_info['formatted_address'], address,
                address_info['location']['lat'], address_info['location']['lng'])

    return sql_args
    
def get_sql_event_args(name, date, meal, start_time, end_time, address, trucks):
    address_info = request_address_info(address)
    event_id = event_name_to_id(name)
    sql_args = (name, date, meal, start_time, end_time, 
                address_info['formatted_address'], address,
                address_info['location']['lat'], address_info['location']['lng'], trucks)

    return sql_args
    
sql_fmt = """INSERT INTO `preview_schedules`(`name`, `truck_id`, `date`, `meal`, `start_time`, `end_time`, `formatted_address`, `address`, `lat`, `lng`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
 
sql_event_fmt = """INSERT INTO `events`(`id`, `date`, `meal`, `start_time`, `end_time`, `formatted_address`, `address`, `lat`, `lng`, `trucks`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

def insert_into_database(name, date, meal, start_time, end_time, address, event_name = None, lat = None, lng = None):
    try:
        #sanity check for the date formate
        a = datetime.strptime(date, '%Y-%m-%d')

	s_time = time.strptime(start_time, "%H:%M:%S")
	e_time = time.strptime(end_time, "%H:%M:%S")
	if e_time < s_time:
	    raise Exception("start_time is later than end_time")
        sql_args = get_sql_args(name, date, meal, start_time, end_time, address.replace("+", " "), lat, lng)
        c.execute(sql_fmt, sql_args)
        if event_name == None:
            event_name = "NULL"
        print "~~~~added one event: %s~~~~~~~" % event_name
        print sql_args
        return True
    except Exception, e: 
        print_error("sql fail (maybe)")
        print "e: %s" %  e
        print name
        print "date:%s" %date
        print "start_time: %s" % start_time
        print "end_time: %s" %end_time
        print "address: %s" %address
        print "meal: %s" %meal
        if e[0] == 1062:
            print "good error!"
            return True
        return False


def check_truck_name (truck_name, output_name):

    try:
        c.execute("""SELECT `name` FROM `all_trucks` WHERE name=%s""", (truck_name,))

	name = c.fetchone()

	if name == None:
	    return False

	else:
	    output_name.append(name['name'])
	    return True

    except Exception, e:
        print_error("sql fail")
	print "e: %s" %e
	print truck_name

	return False

def insert_event_into_database(name, date, meal, start_time, end_time, address, trucks_name = None): 
    try:
        #sanity check for the date formate
        a = datetime.strptime(date, '%Y-%m-%d')
        if trucks_name == None:
            trucks_name = "NULL"
        sql_args = get_sql_event_args(name, date, meal, start_time, end_time, address.replace('+', ' '), trucks_name)
        c.execute(sql_event_fmt, sql_args)
        print "~~~~added one event: %s~~~~~~~" % name
        print sql_args
        return True
    except Exception, e: 
        print_error("sql fail (maybe)")
        print "e: %s" %  e
        print name
        print "date:%s" %date
        print "start_time: %s" % start_time
        print "end_time: %s" %end_time
        print "address: %s" %address
        print "meal: %s" %meal
        print "trucks: %s" %trucks_name
        if e[0] == 1062:
            print "good error!"
            return True
        return False


def decode(html):
    """Returns the given HTML with ampersands, quotes and carets encoded."""
    return html.replace('&amp;',"and").replace('&lt;','<').replace('&gt;','>').replace('&quot;', '"').replace('&#39;', "'").replace('&#039;', "'").replace("&nbsp;", " ")

skip_events = ("close", "private", "grid", "otg", "night market", "busy", "food lounge", "mvbl", "moveable feast", "soma", "truck stop", "truckstop", "no service", "day off", "no cena")

