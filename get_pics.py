import urllib2
import re
import pdb
import sys
import os
import urllib

response = urllib2.urlopen("http://bestfoodtrucksbayarea.com/")

root_html = response.read()

trucks_url_pattern = re.compile(r"""\<a href=\"(?P<truck_url>http:\/\/.*?\/category\/z-food-trucks\/.+?\/)\" \>(?P<truck_name>.+?)\<\/a\>""")

truck_img_pattern = re.compile(r"""data-orig-file=\"(?P<pic>http.+?)\"""")

iter = trucks_url_pattern.finditer(root_html, re.S)

truck_dict = {}
n = 0
for subdir, dirs, files in os.walk("""/lamp/foodtrucksmap/foodtrucksmap/trucks/"""):
    dir_name = os.path.basename(subdir).lower()

    truck_dict[dir_name] = subdir

a = 0
for i in iter:
    n = n+1

    truck_url = i.groupdict()['truck_url']


    truck_name = i.groupdict()['truck_name'].lower().replace(' ', '_')

    if truck_dict.has_key(truck_name):

        #img_iter = truck_img_pattern.finditer(truck_page, re.S)
	#m = 0
        #for j in img_iter:
        #    url = j.groupdict()['pic']
	#    file_name = truck_dict[truck_name] + "/" + os.path.basename(url)
        #    urllib.urlretrieve(url, file_name)
	#    m = m+1


        #print "get the img for" + str(m) + truck_name + " in " + truck_dict[truck_name]
	print "known " +  truck_name

    else:
        print "not known " + truck_name + " " + "/lamp/foodtrucksmap/foodtrucksmap/trucks/tmp/" + truck_name.replace(" ", "_")
	try: os.makedirs("/lamp/foodtrucksmap/foodtrucksmap/trucks/tmp/" + truck_name.replace(" ", "_"))
	except: 
	    print "already there " + truck_name
	    continue

        truck_page = urllib2.urlopen(truck_url).read()
        img_iter = truck_img_pattern.finditer(truck_page, re.S)
	m = 0
        for j in img_iter:
            url = j.groupdict()['pic']
	    file_name =  "/lamp/foodtrucksmap/foodtrucksmap/trucks/tmp/" + truck_name.replace(" ", "_") + "/" + os.path.basename(url)
            urllib.urlretrieve(url, file_name)

     

        



print "total" + str(n)
