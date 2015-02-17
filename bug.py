import re
#import urllib : uncomment this when using LOGIN

from mechanize import Browser
from bs4 import BeautifulSoup


#---------------------------------------------------
LOGIN = "<your email id>"
PASS = "<your password>"
PRI_URL = "https://bugzilla.mozilla.org/"
QRY_URL = "https://bugzilla.mozilla.org/query.cgi/"
BUG_URL = "https://bugzilla.mozilla.org/buglist.cgi/"
ua = 'Mozilla/5.0 (X11; Linux x86_64; rv:18.0) Gecko/20100101 Firefox/18.0 (compatible;)'

br = Browser()
#br.set_all_readonly(False)   
br.set_handle_robots(False)   
#br.set_handle_refresh(False)
br.addheaders = [('User-Agent', ua), ('Accept', '*/*')]

#--------------------------Get availabe status and available products----------------------
response = br.open(QRY_URL)
content = response.read()
soup = BeautifulSoup(content)

# ------------------------------ LOGIN ----------------------------------------

# not necessary for bug reports
'''
print 'Signing into account ...'
print ''

login_data = urllib.urlencode({'Bugzilla_login' : LOGIN, 'Bugzilla_password' : PASS})
f = urllib.urlopen(QRY_URL, login_data)
content = f.read()
#print content
f.close()

print "login successful !!"

soup = BeautifulSoup(content)
span = soup.span
span = span.text[0:14] + span.text[-9:]

print "logged in as :",  span

print ""

print "Reading page source ..."

print ""
'''
#------------------------------------------------------------------------------

response = br.open(QRY_URL)
content = response.read()

available_status = [] #bug status for search

status = soup.find('select', id='bug_status').findAll('option')
for opt in status:
    available_status.append(str(opt.text).lower())
    
#available_status.

available_products = {} #products available for search

prd_list = []
labels = []

products = soup.find('select', id='product').findAll('optgroup')

for prdlbl in products:
    labels.append(prdlbl['label'])


for lbl in labels:
    products = soup.find('select', id='product').find('optgroup', label=lbl).findAll('option')
    for prd in products:
        prd_list.append(prd.text)
    available_products[lbl] = prd_list
    prd_list = []
    
bug_status = []
product = []

print "Done reading"
print ""
print "Search bug database:"
print ""

print "Available status: ", available_status
temp = raw_input('Enter Bug Status : ')
temp = '__' + temp + '__'
bug_status.insert(0, temp)
print ""
print "Available products: "
for x in sorted(available_products):
    print x + ':'
    for y in available_products[x]:
        print y + ',' ,
    print ""
temp = raw_input('Enter Product : ')
product.insert(0, temp)
print ""
content = raw_input('Enter the bug discriptor : ')
print ""

br.select_form(name="queryform")
br.form['bug_status'] = bug_status
br.form['product'] = product
br.form['content'] = content
response = br.submit() 
content = response.read()   

soup = BeautifulSoup(content)
#print soup.prettify()

#-------------BUG IDs and LINKS----------------
id_links = soup.findAll(href=re.compile("show_bug.cgi?"))

#print len(id_links)

temp = []
id_links2 = []
for links in id_links:
    temp.append(links.get('href'))
    
for i in temp:
       if i not in id_links2:
          id_links2.append(i)

print "Total number of bugs found : ", len(id_links2) 
if len(id_links2) == 0:
    print 'No bugs found.'
    print 'Terminating script ...'
    import sys
    sys.exit(0)
print " "
'''
print "Bug IDs:"

for i in range(0, len(id_links2)):
    print id_links2[i][-6:]
'''
print ""
#-----------------------------------

table = soup.find('table', {'class' : 'bz_buglist sortable'})
ID = []
Product = []
Comp = []
Assignee = []
Status = []
Resolution = []
Summary = []
Changed = []

#print table

table_data = []

for row in table.findAll('tr'):
    cols = row.findAll('td')
    if len(cols) == 8:
        ID.append(cols[0].a.string)
        Product.append(cols[1].span.string)
        Comp.append(cols[2].span.string)
        Assignee.append(cols[3].span.string)
        Status.append(cols[4].span.string)
        Resolution.append(cols[5].span.string)
        Summary.append(cols[6].a.string)
        Changed.append(cols[7].string)

for i in range(len(ID)):
    table_data.append(ID[i].rstrip() + " | " + Product[i].rstrip()+ " | " + Comp[i].rstrip() + " | " + Assignee[i].rstrip() + " | " + Status[i].rstrip() + " | " + Resolution[i].rstrip() + " | "+ Summary[i].rstrip() + " | "+ Changed[i].rstrip())

bugs = ()
t = ()
for i in range(len(ID)):
    t = (ID[i].rstrip(),) + (Product[i].rstrip(),) + (Comp[i].rstrip(),) + (Assignee[i].rstrip(),) + (Status[i].rstrip(),) + (Resolution[i].rstrip(),) + (Summary[i].rstrip(),) + (Changed[i].rstrip(),)
    bugs = bugs + (t,)

#print bugs

bug_url = []
for links in id_links2:
    temp = PRI_URL+links
    bug_url.append(temp)
'''
print "Bug URLs:" 
   
for bug in bug_url:
    print bug
'''
print " " 

print "Scrapping each page corresponding to bugs found ..."

#--------------------------------------Scrapping each page corresponding to a bug----------------------------------------
'''
#can parse the returned content list 'div' to get bug_number and bug_description

div = soup.find('div', {'class' : 'bz_alias_short_desc_container edit_form'}).contents
print div
'''
# can also use SoupStrainer to do this
# dictionary for all bugs
comp_bug_dict = dict()
# dicionary of one bug
bug_dict = dict()

for i in range(len(bug_url)):
    response = br.open(bug_url[i])
    content = response.read()
    soup = BeautifulSoup(content)
    bug_number = soup.find('div', {'class' : 'bz_alias_short_desc_container edit_form'}).find('a', href=re.compile("show_bug")).find('b').text
    super_key = str(bug_number[-6:]) # key for complete bug dictionary    
    bug_number = bug_number[0:3] + " " + bug_number[-6:]
    bug_descriptor = soup.find('div', {'class' : 'bz_alias_short_desc_container edit_form'}).find('span', id='short_desc_nonedit_display').text
    title = bug_number + " " + bug_descriptor
    # bug description table is divided into two columns, each of these columns contains a table
    # left column
    table_column_1_rows = soup.find('td', id='bz_show_bug_column_1').find('table').findAll('tr')

    # dictionary to hold table fields and their value as key-value pairs
    left_dict = dict()
    for tr in table_column_1_rows:
        th = tr.findAll('th')
        if(len(th) != 0): # some rows are left blank(to provide space between portions of table)
            key = th[0].text.replace("&nbsp;", " ")
            key = str(re.sub(r"\s+", " ", key))
            td = tr.findAll('td')
            value = str(td[0].text.replace("&nbsp;", " "))
            if(len(value) > 50): # text returns javascript text also .... this resolves it 
                value = value[:16]
                value = str(re.sub(r"\s+", " ", value))
            key = key.strip(':')
            value = value.strip(':')    
            value = value.replace("\n", "")
            if(key != ' ' and key != 'Duplicates'): # one of the key-value pair is : ' ': show dependency graph, which is not needed
                ''' some bug page tabels contain  a 'Duplicate' field', presence of this in some pages causes problems when writing to database as the list that is written to the db contains this field for some and not for others and hence causes incorrect binding error when writing to database.
                this is a temporary and naive fix.
                '''
                left_dict[key] = value
                
            #print 'Key: ', key, ' Value: ', value, '\n'
    #print 'left dict', left_dict
            
    #right column
    table_column_2_rows = soup.find('td', id='bz_show_bug_column_2').find('table').findAll('tr')

    # dictionary to hold table fields and their value as key-value pairs
    right_dict = dict()
    for tr in table_column_2_rows:
        th = tr.findAll('th')
        if(len(th) != 0): # some rows are left blank(to provide space between portions of table)
            key = th[0].text.replace("&nbsp;", " ")
            key = str(re.sub(r"\s+", " ", key))
            td = tr.findAll('td')
            value = str(td[0].text.replace("&nbsp;", " "))
            if(len(value) > 50): # text returns javascript text also .... this resolves it 
                value = value[:16]
                value = str(re.sub(r"\s+", " ", value))
            key = key.strip(':')
            value = value.strip(':')
            value = value.replace("\n", "")
            if(key != ' '):# one of the key-value pair is : ' ': show dependency graph, which is not needed
                right_dict[key] = value
    #print right_dict    
    
    # merging two dictionaries        
    bug_dict.clear()
    bug_dict.update(left_dict)    
    bug_dict.update(right_dict)
    #print bug_dict
    super_key = super_key.strip()
    value = str(bug_dict).strip()   
    comp_bug_dict[super_key] = value
    #print 'complete dictionary', comp_bug_dict    
    # write to file after each iteration
    '''
        print ""
        print "opening file ..."
        fp = open('bug report temp.txt', "a")
        print "Writing bug description reports to file" ,fp.name
        fp.write("%s\n" % title)
        fp.write(str(bug_dict))
        print "Bug report written"
        print "closing file"
        fp.close()
        print ""
    '''
print "done"
print ""    
    #print 'Key: ', key, ' Value: ', value, '\n'   

#print '\n\nCOMPLETE DICTIONARY\n\n',comp_bug_dict
#--------------------------------------Writing to text file----------------------------------------
print ""
print "opening file ..."
fp = open('bug report.txt', "w")
print "Writing bug description reports to file" ,fp.name
fp.write(str(comp_bug_dict))
print "Bug report written"
print "closing file"
fp.close()
print ""
#--------------------------------------------------------------------------------------------------

#--------------------------------------Writing bug reports to database-----------------------------
print ""
print "Connecting to database ..."

import sqlite3 as sql
connection = None
connection = sql.connect('bug.db')

#connecting to database and getting fetched resources database ready

print "Connected"
print "Writing to database ..."
# manipulating comp_bug_dict to write to database
extra_id = '#BugID' # adds BugID field to database table of bug description
wrt_to_db_field_list = [] #field of db table 'description'
wrt_to_db_field_list.append(extra_id)
for key in bug_dict.iterkeys():
    wrt_to_db_field_list.append(str(key))
    
  
import ast # needed for ast.literal_eval
#temp = ast.literal_eval(a) # converts a string(a string rep of a dict) to dict

wrt_to_db_value_list = [] #key and value of comp_bug_dict as a list, to write into db

for key, value in comp_bug_dict.items():
    tup = ()
    temp = []    
    tup = (extra_id, str(key))
    #print '\nTUPLE 1\n', tup
    temp.append(tup)
    for tkey, tval in ast.literal_eval(value).items():
        tup = (str(tkey), str(tval))
        #print '\nTUPLE 2\n', tup
        temp.append(tup)
    #print '\nTEMP\n', temp    
    wrt_to_db_value_list.append(temp)
    #print '\nVALUES\n', wrt_to_db_value_list
    
wrt_to_db_field_list.sort()
wrt_to_db_value_list.sort()
#print '\n\nFIELDS', len(wrt_to_db_field_list), '\n\n' 
#print '\n\nVALUES', wrt_to_db_value_list, '\n\n'

wrt_to_db = [] # list of lists: values to write to db
for val in wrt_to_db_value_list:
    temp = []
    for each_val in sorted(val):
        #print '\n\nEACH VALUE', each_val
        temp.append(str(each_val[1]))
    wrt_to_db.append(temp)
'''
print '\n\nWRITE TO DB\n\n', wrt_to_db
print '\n\nWRITE TO DB\n\n', len(wrt_to_db[0]), len(wrt_to_db[1]), len(wrt_to_db[2]), len(wrt_to_db[3]), len(wrt_to_db[4])

for i in wrt_to_db:
    j = 1
    for k in i:
        print j, ':', k
        j = j+1
'''
'''
FIELDS [' ', 'Assigned To', 'Blocks', 'BugID', 'CC List', 'Classification', 'Component', 'Crash Signature', 'Depends on', 'Importance', 'Keywords', 'Modified', 'Platform', 'Product', 'QA Contact', 'Reported', 'See Also', 'Status', 'Target Milestone', 'URL', 'Version', 'Whiteboard'] 

'''    
    
with connection:
    
    cur = connection.cursor() 
    #---------------
    # one time ... overwrites table content each time the script is run    
    cur.execute("DROP TABLE IF EXISTS Bugs")
    cur.execute("CREATE TABLE Bugs(Id TEXT PRIMARY KEY, Product TEXT, Comp TEXT, Assignee TEXT, Status TEXT, Resolution TEXT, Summary TEXT, Changed TEXT)")
    cur.executemany("INSERT INTO Bugs VALUES(?, ?, ?, ?, ?, ?, ?, ?)", bugs)
    #----------------
    '''
    cur.execute("DROP TABLE IF EXISTS bug_des")
    cur.execute("create table bug_des (key text, value integer);")
    cur.executemany("insert into bug_des values (?,?);", comp_bug_dict.iteritems())
    '''
    cur.execute("CREATE TABLE IF NOT EXISTS Description ('#BugID' TEXT PRIMARY KEY, 'Assigned To' TEXT, 'Blocks' TEXT, 'CC List' TEXT, 'Classification' TEXT, 'Component' TEXT, 'Crash Signature' TEXT, 'Depends on' TEXT, 'Importance' TEXT, 'Keywords' TEXT, 'Modified' TEXT, 'Platform' TEXT, 'Product' TEXT, 'QA Contact' TEXT, 'Reported' TEXT, 'See Also' TEXT, 'Status' TEXT, 'Target Milestone' TEXT, 'URL' TEXT, 'Version' TEXT, 'Whiteboard' TEXT)")
    cur.executemany("INSERT or REPLACE INTO Description VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", wrt_to_db)
    #cur.executemany("INSERT INTO Description VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", wrt_to_db)                  
    connection.commit()
print "Database updated"   
print ""
#------------------------------------------Pickle-------------------------------------
# one time ... overwrites file each time the script is run
print "dumping to pickle file..."

import pickle

pickle.dump( comp_bug_dict, open( "bug.p", "wb" ) )

print "done"
temp = pickle.load( open( "bug.p", "rb" ) )
print ""
#-------------------------------------------------------------------------------------
#------------------------------------------------------JSON---------------------------
# one time ... overwrites file each time the script is run
print "dumping to JSON file ..."
import json

with open('bug.json', 'w') as f:
    json.dump(comp_bug_dict, f)

print "done"

with open('bug.json') as f:
    comp_bug_dict = json.load(f)
#-------------------------------------------------------------------------------------
