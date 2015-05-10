import urllib2
import re
import pdb
import MySQLdb
import MySQLdb.cursors 
import sys
import os


conn=MySQLdb.connect(host="localhost",user="ft",passwd="",db="foodtrucks", cursorclass=MySQLdb.cursors.DictCursor)

c = conn.cursor()

response = urllib2.urlopen("http://offthegridsf.com/vendors")

html = response.read()

# we only care about food trucks
food_trucks_pattern = re.compile(r'<div class=\"otg-vendor-type-name\">Trucks</div>.*?<div class=\"otg-vendor-type otg-vendor-type-1\">', re.S)

# to match each truck 
truck_pattern = re.compile(r'class=\"otg-vendor-logo\" src=\"(?P<logo>.*?)\".*?a class=\"otg-vendor-name-link\" href=\"(?P<url>.*?)\" target=\"_blank\">(?P<name>.*?)</a>.*?<div class=\"otg-vendor-cuisines\">\s+?(?P<category>.*?)</div>', re.S)

iter = truck_pattern.finditer(food_trucks_pattern.search(html, re.S).group(), re.S)

a=0
fail = 0
for i in iter:
    a = a+1
    name = i.groupdict()['name'].replace('\t','').replace('\n','').replace('&#039;', '\'').replace('&amp;','&')
    name = re.sub(r' $', "", name)
    path_name = name.replace(' ', '_')
    os.mkdir("./%s"%path_name, 755)

    
    category = i.groupdict()['category'].replace('\t','').replace('\n','').replace(' ','').replace('Fusion', '')
    detail = i.groupdict()['category'].replace('\t','').replace('\n','')
    logo = i.groupdict()['logo'].replace('\t','').replace('\n','')
    
    try:
        logo_file = urllib2.urlopen(logo)

        # Open our local file for writing
        with open(path_name+"/"+os.path.basename(logo), "wb") as local_file:
            local_file.write(logo_file.read())

    #handle errors
    except HTTPError, e:
        print "HTTP Error:", e.code, logo, logo_file
    except URLError, e:
        print "URL Error:", e.reason, logo, logo_file


    url = i.groupdict()['url']
    sql = """INSERT INTO `all_trucks`(`name`, `category`, `logo`, `url`, `category detail`) VALUES (%s,%s,%s,%s,%s)"""
    args = (name, category, logo, url, detail)
    try: 
        c.execute(sql, args)
        c.execute("""show warnings""")
        w = c.fetchone()
        if w and w['Message'] == "Data truncated for column 'category' at row 1" :
            category = category + ",other"
            sql = """UPDATE `foodtrucks`.`all_trucks` SET `category` = %s WHERE `all_trucks`.`name` = %s"""
            args = (category, name)
            c.execute(sql, args)
            c.execute("""show warnings""")
            w = c.fetchone()
            if w and w['Message'] != "Data truncated for column 'category' at row 1":
                raise Exception("shit")
    except Exception, e: 
        fail = fail + 1
        print "~~~~~~error:~~~~~~~"
        print e
        print sql
        print args

print "~~~~~~~~~~DONE~~~~~~~~~~"
print "total: %s" % a
print "failed : %s" % fail

