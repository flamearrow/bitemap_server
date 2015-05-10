import urllib2
import re
import shutil
import pdb
import MySQLdb
import MySQLdb.cursors 
import sys
import os

conn=MySQLdb.connect(host="localhost",user="ft",passwd="",db="foodtrucks", cursorclass=MySQLdb.cursors.DictCursor)

c = conn.cursor()

sql = """select * from `all_trucks`"""

c.execute(sql)
w = c.fetchall()
truck_page_template = "/lamp/foodtrucksmap/foodtrucksmap/truck.php"

large_img_template = """
	<li>
		<a href="img_path" class="highslide" title="img_name" 
			onclick="return hs.expand(this, config1 )">
			<img src="thumb_path"  alt="img_name"/>
		</a>
	</li>
"""

small_img_template = """
"""
extensions = {"jpg", "png", "gif", "jpeg"}

for truck in w:
    truck_name = truck['name']
    truck_category = truck['category']
    name = truck['name']
    name = re.sub(r'\W', "_", name)
    truck_path_name = name.replace(' ', '_')
    if not os.path.exists("/lamp/foodtrucksmap/foodtrucksmap/trucks/" + truck_path_name):
        print truck_path_name
	print "FAIL~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
	continue


    truck_dir = "/lamp/foodtrucksmap/foodtrucksmap/trucks/" + truck_path_name
    truck_dir_path = "/trucks/" + truck_path_name

    truck_page_path = truck_dir + "/truck.php"
    if not os.path.exists(truck_page_path):
	shutil.copy(truck_page_template, truck_page_path)
        truck_page = open(truck_page_template,"r")
	page = truck_page.read()
	truck_page.close()
	img_files = []

	for f in os.listdir(truck_dir):
	    if os.path.isfile(truck_dir + '/' + f):
	        if any (extension in f.lower() for extension in extensions): 
	            print "find a img flie " + f.lower()
	            img_files.append(f.lower())

                else:
	            print "not img file " + f.lower() 
        

        large_img_buffer = ""
	for file_src in img_files:
	    img_name = os.path.basename(file_src).replace("_", " ").replace("-", " ").replace("\.*", "")
	    new_large_img = large_img_template.replace("img_path", truck_dir_path + '/reduced/' + file_src).replace("img_name", img_name).replace("thumb_path", truck_dir_path + """/thumb/""" + file_src)
	    large_img_buffer = large_img_buffer + '\n' + new_large_img 


        truck_page = open(truck_page_path,"w")
	page = re.sub("truck_path_name", truck_path_name, page)
	page = re.sub("truck_name", truck_name, page)

	page = page.replace("""<large_img_holder>""", large_img_buffer)
	truck_page.write(page)
	truck_page.close()
