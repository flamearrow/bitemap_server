import httplib2
import pdb
import argparse
from datetime import timedelta, datetime, tzinfo, time
import urllib2
import re
import sys
import lib

import MySQLdb
import MySQLdb.cursors 

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run




parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--cID', type=str, dest='calendarId', action='store', help='calendarId')
#parser.add_argument('--from', type=str, dest='startDay', action='store',help='start date', required=True)
#parser.add_argument('--to', type=str, dest='endDay', action='store',help='end date', required=True)
parser.add_argument('--name', type=str, dest='name', action='store',help='truck name', required=True)
parser.add_argument('--url', type=str, dest='url', action='store',help='website url')

args = parser.parse_args()
total = 0
fail = 0
skip = 0
success = 0

lib.start(args.name, args.url)
calendarId = args.calendarId
if not calendarId:
    url = args.url
    
    html = lib.get_url_content(url)

    if html == "":
        lib.finish(args.name, args.url)
    
    google_calendar_pattern = re.compile(r'https://www.google.com/calendar.*?src=(?P<cID>[0-9a-zA-Z].*?((%40)|@).*?\.com)')
    
    
    try: calendarId = google_calendar_pattern.search(html).groupdict()['cID'].replace("%40", "@")
    except Exception, e: 
        lib.print_error("fail to get calendar ID")
        print e
        lib.finish(args.name, args.url)


print "~~~~~~~calendarID:%s ~~~~~~~~~~" %calendarId
    

FLOW = OAuth2WebServerFlow(
    client_id='154781234816-h5nmu0iuq3do0tsga33km22g2t0al0ru.apps.googleusercontent.com',
    client_secret='JRwb4_2ZXMe8iTf6t6GazJbD',
    scope='https://www.googleapis.com/auth/calendar.readonly',
    user_agent='test/0.1')

storage = Storage('../calendar.dat')
credentials = storage.get()
if credentials is None or credentials.invalid == True:
  credentials = run(FLOW, storage)

# Create an httplib2.Http object to handle our HTTP requests and authorize it
# with our good Credentials.
http = httplib2.Http()
http = credentials.authorize(http)

# Build a service object for interacting with the API. Visit
# the Google Developers Console
# to get a developerKey for your own application.
service = build(serviceName='calendar', version='v3', http=http,
                   developerKey='AIzaSyAv11A9OptZ5TX-Pqr3egpbddHQzQ_yULU')

# open database
db = MySQLdb.connect(host="localhost",user="ft",passwd="",db="foodtrucks", cursorclass=MySQLdb.cursors.DictCursor, sql_mode="STRICT_ALL_TABLES")

c = db.cursor()
#calendarId = 'rh7m6jon48l6ta3c1lpisle820@group.calendar.google.com'

#startTime = datetime.strptime(args.startDay, "20%y-%m-%d").isoformat()+"-0700"

# from today
startTime = datetime.now().replace(microsecond=0).isoformat()+"-0700"

# endTime is 7 days later than startTme  not include
endTime = (datetime.now().replace(microsecond=0) + timedelta(days=7)).isoformat()+"-0700"
#endTime = (datetime.strptime(args.startDay, "20%y-%m-%d") + timedelta(days=7)).isoformat()+"-0700"

name = args.name

page_token = None

while True:
    events = service.events().list(calendarId=calendarId, pageToken=page_token, timeMin=startTime, timeMax=endTime, singleEvents=True).execute()
    for event in events['items']:
        start_date = None
        end_date = None
        date = None
        start_time = None
        end_time = None
        address = None
        meal = None
        sql_args = None
        formatted_address = None

        total = total + 1

        try: event_name = event['summary']
        except:   
            print "~~~~~~skip: no event summary~~~~~~~"
            print event
            skip = skip +1
            continue

        if any(skip_event in event['summary'].lower() for skip_event in lib.skip_events):
            print "----skip----"
            print event['summary']
            skip = skip + 1
            continue

        try: 
            # special handle for daylight saving..  I know it is stupid
            if event['start']['dateTime'][-4] == '7': 
                start_date = datetime.strptime(event['start']['dateTime'], "20%y-%m-%dT%H:%M:%S-07:00")
            else:
                start_date = datetime.strptime(event['start']['dateTime'], "20%y-%m-%dT%H:%M:%S-08:00")
            if event['end']['dateTime'][-4] == '7': 
                end_date = datetime.strptime(event['end']['dateTime'], "20%y-%m-%dT%H:%M:%S-07:00")
            else:
                end_date = datetime.strptime(event['end']['dateTime'], "20%y-%m-%dT%H:%M:%S-08:00")
            date = start_date.strftime("20%y-%m-%d")
            start_time = start_date.strftime("%H:%M:00")
            end_time = end_date.strftime("%H:%M:00")
            
            try: address = event['location']
            except: address = event['summary']

            if "@" in address:
                # remove the @ and front part
                address = address[address.find("@")+1:]

            if start_date.time() < time(14):
                meal = "lunch"
            else:
                meal = "dinner"

            ret_ok = lib.insert_into_database(name, date, meal, start_time, end_time, address, event['summary'])
            if ret_ok == True:
                success = success + 1
            else:
                fail = fail + 1
        except Exception, e: 
            fail = fail + 1
            lib.print_error("unexpected error")
            print "e: %s" %  e
            print "event %s" %event
            print "start_date %s " %start_date
            print "end_date: %s" %end_date
            print "date:%s" %date
            print "start_time: %s" % start_time
            print "end_time: %s" %end_time
            print "address: %s" %address
            print "meal: %s" %meal
    page_token = events.get('nextPageToken')
    if not page_token:
        break

lib.finish(name= args.name, url = args.url, total = total, fail = fail, skip = skip, success=success)
