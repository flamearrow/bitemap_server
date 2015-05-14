import json
import re
import requests
import xml.etree.ElementTree as EleT

"""
Crawl off the grid website for their weekly schedules

The script will go though OTGMarketsJson.json(which is parsed from source of http://offthegridsf.com/markets)
For each of its id and use 'http://offthegridsf.com/wp-admin/admin-ajax.php?action=otg_market&delta=0&market='
to pull all schedules of THIS week. Result is written to out.json as a list of following event objects:
{
    "end":"0900", "latitude":"37.415237",
    "longitude":"-122.077637",
    "start":"1700",
    "address":"1401 North Shoreline Boulevard , Mountain View",
    "date":"0515", "truck_name":"Gold Rush Eatery"
}
"""

REQ_BASE = 'http://offthegridsf.com/wp-admin/admin-ajax.php?action=otg_market&delta=0&market=%s'

STR_MAP = {
        '#039;': '\''
}

def get_json():
    """
    stupidly parse the source and encode json from http://offthegridsf.com/markets
    :return: json dictionary
    """
    resp = requests.get("http://offthegridsf.com/markets").content
    for line in resp.splitlines():
        if "OTGMarketsJson" in line:
            json_data = re.search(r".*OTGMarketsJson = '(?P<dat>.*)';</script>", line).groupdict()
            return json.loads(json_data['dat'].replace('\\', ''))
    return None


def parse_request(req, lat, lng):
    resp = requests.get(req).content

    def do_replace(name):
        for key in STR_MAP:
            if key in name:
                return name.replace(key, STR_MAP[key])
        return name

    def build_time(time_int):
        if time_int < 8:
            time_int = int(time_int) + 12
            return str(time_int) + "00"
        elif time_int < 10:
            return "0" + str(time_int) + "00"
        else:
            return str(time_int) + "00"

    invalid_str0 = '&'
    resp = resp.replace(invalid_str0, '')

    root = EleT.fromstring(resp)

    event_time_node = root[0][1][2]
    event_address_node = root[0][0][0][2][0]
    event_address = event_address_node.text
    event_count = len(event_time_node)

    # print "there're " + str(event_count) + " events"

    event_result = []

    event_date_base = 2
    for i in range(event_count):
        # print "---event " + str(i)
        offset = i * 2
        event_date_node = root[0][event_date_base + offset]
        event_date = event_date_node.text.strip().replace('.', '')
        # print "date:" + event_date
        # print "time" + event_time_node[i][1].text
        times = event_time_node[i][1].text.split('-')
        start_time = build_time(int(times[0]))
        end_time = build_time(int(times[1]))
        # print 'start: ' + build_time(int(times[0]))
        # print 'end: ' + build_time(int(times[1]))
        event_vendors_node = root[0][event_date_base + offset + 1]
        for child in event_vendors_node[1]:
            new_event = {}
            truck_name = do_replace(child[0].text)
            new_event['truck_name'] = truck_name
            new_event['address'] = event_address
            new_event['date'] = event_date
            new_event['start'] = start_time
            new_event['end'] = end_time
            new_event['latitude'] = lat
            new_event['longitude'] = lng
            event_result.append(new_event)
    return event_result


def parse_all():
    """
    crawl data from OTG website and return them

    :return: dictionary of event schedules in the following format
    {
        "end":"0900", "latitude":"37.415237",
        "longitude":"-122.077637",
        "start":"1700",
        "address":"1401 North Shoreline Boulevard , Mountain View",
        "date":"0515", "truck_name":"Gold Rush Eatery"
    }
    """
    markets = get_json()
    ret = []
    for key in markets:
        print "processing key " + key
        json_result = parse_request(REQ_BASE % key, markets[key]['latitude'], markets[key]['longitude'])
        ret.extend(json_result)
    return ret


def parse_all_to_file():
    """
    crawl and write result to out.json
    """
    final_result = parse_all()

    with open('out.json', 'w') as json_out:
        json.dump(final_result, json_out, indent=4, separators=(',', ':'))
    print "result written to out.json"


parse_all_to_file()