#__author__ = 'chanakya'
from __future__ import division
import csv
import urllib2
#import StringIO
import sqlite3 as sql
from xml.dom import minidom
from pprint import pprint
#import requests
#import xml.etree.ElementTree as ET
from database import DatabaseOperation
#from collections import defaultdict


class BugReport:
    def __init__(self):
        self.base_URL = 'https://bugs.eclipse.org/bugs/buglist.cgi?'
        self.xml_URL = 'https://bugs.eclipse.org/bugs/show_bug.cgi?ctype=xml&id='
        self.ext_URL = 'query_format=advanced&'
        self.csv_URL = 'ctype=csv&human=0'

        self.bug_ID = []
        self.bug_xml_URL = {}

    def search_parameters(self, classification, product, component, status,
                          resolution):  # parameters for searching bug repository
        self.classification = classification
        self.product = product
        self.componemt = component
        self.status = status
        self.resolution = resolution

        self.URL_builder()

    def URL_builder(self):  # builds query/search url based on search parameters
        status = classification = component = resolution = product = ''
        for i in self.status:
            status += 'bug_status=' + i + '&'
        for i in self.classification:
            classification += 'classification=' + i + '&'
        for i in self.componemt:
            component += 'component=' + i + '&'
        for i in self.resolution:
            resolution += 'resolution=' + i + '&'
        for i in self.product:
            product += 'product=' + i + '&'

        search_URL = (self.base_URL + status + classification + component + product + self.ext_URL + resolution + self.csv_URL).encode('utf-8')
        print search_URL

        self.get_CSV(search_URL)

    def get_CSV(self, search_URL):  # saves the csv response(gotten by opening search_URL) to a file
        response = urllib2.urlopen(search_URL)
        csv_read = csv.reader(response)
        with open('test1.csv', 'wb') as test_file:
            csv_write = csv.writer(test_file)
            for row in csv_read:
                csv_write.writerow(row)
                #print row
        self.get_bug_ID_from_CSV('test1.csv')

    def get_bug_ID_from_CSV(self,
                            file_name):  # takes the csv file(which contains bug info) as input and saves bug id(column 1) from it to a list
        with open(file_name, 'rb') as csvfile:
            csv_read = csv.reader(csvfile)
            csv_read.next()
            for row in csv_read:
                self.bug_ID.append(row[0])

        self.generate_bug_xml_url()

    def generate_bug_xml_url(self):  # creates a dictionary(bug_xml_URL), with bug_id as key and xml_url as value
        for id in self.bug_ID:
            self.bug_xml_URL[id] = self.xml_URL + str(id)
        #print self.bug_xml_URL
        self.create_xml_from_url()

    def create_xml_from_url(self):  # opens every url from bug_xml_url and saves each response as '<bug_id>'.xml
        #print self.bug_xml_URL.items()
        for fname, url in self.bug_xml_URL.items():
            print fname, url
            response = urllib2.urlopen(url)
            xml_response = minidom.parse(response).toxml('utf-8')
            #for element in xml_response.getElementsByTagName('thetext'):
            #    print element.firstChild.nodeValue
            #print xml_response.toprettyxml()
            f = open(fname + ".xml", "wb")
            f.write(xml_response)
            f.close()


if __name__ == '__main__':
    '''
    #-------------- Take as user input ---------------
    classification = ['Eclipse', ]
    product = ['Platform', ]
    component = ['IDE', 'Resources', ]
    status = ['CLOSED', ]
    resolution = ['FIXED', ]

    #-------------------------------------------------

    bug_report = BugReport()
    bug_report.search_parameters(classification, product, component, status, resolution)
    '''
    #----------------- Parse saved xml files and store content in database --------------------------------

    dbdir = '/home/chanakya/PycharmProjects/Eclipse Bug Reports'
    ans = raw_input('Parse XML Files and add to database ? ')
    if int(ans):
        #from database import DatabaseOperation
        db = DatabaseOperation(dbdir)
        db.parse_files_and_populate()
    else:
        pass

    #---------------------------- Data Pre-processing -----------------------------------------------

    ans = raw_input('Perform data preprocecsing ? ')
    clean_stem_id_token = {}
    bug_report_text = {}
    if int(ans):
        from preprocessing import TextPreprocessing
        dp = TextPreprocessing('EclipseBugReports.db')
        bug_report_text = dp.connect_to_db()
        clean_stem_id_token = dp.noise_reducer()
    else:
        pass
    #print clean_stem_id_token
    '''
    '''
    for bid in bug_report_text.keys():
        print bug_report_text[bid]
        for sentence in clean_stem_id_token[bid]:
            print sentence
        break
    '''
    '''
    #dbobj = DatabaseOperation('')
    #dbobj.write_to_database('EclipseBugReports.db', 'table2', clean_stem_id_token)

    connection = sql.connect('EclipseBugReports.db')
    #get_query = 'SELECT short_desc FROM table1 WHERE ID = '
    query = 'INSERT into table2(bug_id, clean_text) VALUES(?, ?)'
    for key, val in clean_stem_id_token.items():
        values = (key, str(val))
        #print values
        if connection.execute(query, values) is None:
            print 'Db connection none'
    connection.commit()
    connection.close()

    #-------------------------------------------------------------------------------

    connection = None
    try:
        connection = sql.connect('EclipseBugReports.db')
    except BaseException, ex:
        print str(ex)

    query = 'select bug_id, clean_text from table2'
    result = connection.execute(query)
    temp = {}

    if result is None:
        print 'result none'

    for row in result.fetchall():
        temp[row[0]] = row[1]

    connection.commit()
    connection.close()

    #--------------------------- Feature Vectors ---------------------------------

    ans = raw_input('Calculate Sentence Feature Values ? ')
    if int(ans):
        col_names = ['bug_id', 'short_desc']
        from feature_scoring import Features
        feature_obj = Features('', 'EclipseBugReports.db')
        feature_obj.get_required_resources(col_names)

        sentences_score_vector = []
        id_to_sentences_score_vector = {}

        for bid, sentences in clean_stem_id_token.items():
            id_to_sentences_score_vector.update(feature_obj.get_score_vector({bid: sentences}))

        #print id_to_sentences_score_vector['189823']
        connection = sql.connect('EclipseBugReports.db')
        #get_query = 'SELECT short_desc FROM table1 WHERE ID = '
        query = 'INSERT into table3(bug_id, FSV) VALUES(?, ?)'
        for key, val in id_to_sentences_score_vector.items():
            values = (key, str(val))
            #print values
            if connection.execute(query, values) is None:
                print 'Db connection none'
        connection.commit()
        connection.close()
        #print '--------------------------------------------------------------------------------------------------------'
        #print temp['189823']
    else:
        pass

    #------------------------------------------------------------------------------------------------------------------
    def normalize(n, _min, _max):
        x = (float(n) - float(_min))/(float(_max) - float(_min))
        if x > 1.0:
            print n, _min, _max, x
        return x
    #------------------------------ Normalize Feature Vectors ---------------------------------------------------------
    ans = raw_input('Normalize Sentence Feature Values ? ')
    if int(ans):
        connection = None
        try:
            connection = sql.connect('EclipseBugReports.db')
        except BaseException, ex:
            print str(ex)

        query = 'select bug_id, FSV from table3'
        result = connection.execute(query)
        id_to_sentences_score_vector = {}

        if result is None:
            print 'result none'

        for row in result.fetchall():
            #print 'ROW: ', row[1]
            #row[1]: u'[[0.75, 0.32, 0.7668666902075585, 19.913901323721589, 0.0625, 1, 0.0],
            #  [0.0, 0.2, 0.313549421592915, 20.160724638695015, 0.1, 1, 0.0]]'
            temp = (row[1][1:len(row[1]) - 1])
            #(row[1][1:len(row[1])-1]): u'[0.75, 0.32, 0.7668666902075585, 19.913901323721589, 0.0625, 1, 0.0],
            #  [0.0, 0.2, 0.313549421592915, 20.160724638695015, 0.1, 1, 0.0]'
            #print 'TEMP: ', temp
            #for i in range(0, len(temp)):
            #    open = temp.find('[')
            #id_to_sentences_score_vector[row[0]] = (row[1][1:len(row[1])-1])
            opn = [i for i, ltr in enumerate(temp) if ltr == '[']
            close = [i for i, ltr in enumerate(temp) if ltr == ']']
            #print 'OPEN: ', opn
            #print 'CLOSE: ', close
            temp_list_of_list = []
            for i in range(0, len(opn)):
                temp_list = (temp[opn[i] + 1:close[i]]).split(',')
                #print 'Temp List: ', temp_list
                #temp_list: [u'0.75', u' 0.32', u' 0.7668666902075585', u' 19.913901323721589', u' 0.0625', u' 1', u' 0.0']
                temp_list_of_list.append(temp_list)
            id_to_sentences_score_vector[row[0]] = temp_list_of_list
        connection.commit()
        connection.close()
        score_1 = []
        score_2 = []
        score_3 = []
        score_4 = []
        score_5 = []
        score_6 = []
        score_7 = []
        score_8 = []
        for key, values in id_to_sentences_score_vector.items():
            for value in values:
                #print key, value
                score_1.append(value[0])
                score_2.append(value[1])
                score_3.append(value[2])
                score_4.append(value[3])
                score_5.append(value[4])
                score_6.append(value[5])
                score_7.append(value[6])
                score_8.append(value[7])

        min_score_1 = min(score_1, key=float)
        max_score_1 = max(score_1, key=float)
        min_score_2 = min(score_2, key=float)
        max_score_2 = max(score_2, key=float)
        min_score_3 = min(score_3, key=float)
        max_score_3 = max(score_3, key=float)
        min_score_4 = min(score_4, key=float)
        max_score_4 = max(score_4, key=float)
        min_score_5 = min(score_5, key=float)
        max_score_5 = max(score_5, key=float)
        min_score_6 = min(score_6, key=float)
        max_score_6 = max(score_6, key=float)
        min_score_7 = min(score_7, key=float)
        max_score_7 = max(score_7, key=float)
        min_score_8 = min(score_8, key=float)
        max_score_8 = max(score_8, key=float)

        id_to_nor_sentences_score_vector = {}
        for key, values in id_to_sentences_score_vector.items():
            comp_normalized_vector = []
            for value in values:
                normalized_vector = []
                normalized_vector.append(normalize(value[0], min_score_1, max_score_1))
                normalized_vector.append(normalize(value[1], min_score_2, max_score_2))
                normalized_vector.append(normalize(value[2], min_score_3, max_score_3))
                normalized_vector.append(normalize(value[3], min_score_4, max_score_4))
                normalized_vector.append(normalize(value[4], min_score_5, max_score_5))
                normalized_vector.append(normalize(value[5], min_score_6, max_score_6))
                normalized_vector.append(normalize(value[6], min_score_7, max_score_7))
                normalized_vector.append(normalize(value[7], min_score_8, max_score_8))
                comp_normalized_vector.append(normalized_vector)
            id_to_nor_sentences_score_vector[key] = comp_normalized_vector
        #pprint(id_to_nor_sentences_score_vector)

        connection = sql.connect('EclipseBugReports.db')
        query = 'INSERT into table4(bug_id, NFSV) VALUES(?, ?)'
        for key, val in id_to_nor_sentences_score_vector.items():
            values = (key, str(val))
            #print values
            if connection.execute(query, values) is None:
                print 'Db connection none'
        connection.commit()
        connection.close()

        #------------------------------

        connection = sql.connect('EclipseBugReports.db')
        query = 'select bug_id, NFSV from table4'
        result = connection.execute(query)
        id_to_sentences_score_vector = {}

        if result is None:
            print 'result none'

        for row in result.fetchall():
            temp = (row[1][1:len(row[1]) - 1])
            opn = [i for i, ltr in enumerate(temp) if ltr == '[']
            close = [i for i, ltr in enumerate(temp) if ltr == ']']
            temp_list_of_list = []
            for i in range(0, len(opn)):
                temp_list = (temp[opn[i] + 1:close[i]]).split(',')
                temp_list_of_list.append(temp_list)
            id_to_sentences_score_vector[row[0]] = temp_list_of_list
        connection.commit()
        connection.close()
        score_1 = []
        score_2 = []
        score_3 = []
        score_4 = []
        score_5 = []
        score_6 = []
        score_7 = []
        score_8 = []
        for key, values in id_to_sentences_score_vector.items():
            for value in values:
                #print key, value
                score_1.append(value[0])
                score_2.append(value[1])
                score_3.append(value[2])
                score_4.append(value[3])
                score_5.append(value[4])
                score_6.append(value[5])
                score_7.append(value[6])
                score_8.append(value[7])

        min_score_1 = min(score_1)
        max_score_1 = max(score_1)
        min_score_2 = min(score_2)
        max_score_2 = max(score_2)
        min_score_3 = min(score_3)
        max_score_3 = max(score_3)
        min_score_4 = min(score_4)
        max_score_4 = max(score_4)
        min_score_5 = min(score_5)
        max_score_5 = max(score_5)
        min_score_6 = min(score_6)
        max_score_6 = max(score_6)
        min_score_7 = min(score_7)
        max_score_7 = max(score_7)
        min_score_8 = min(score_8)
        max_score_8 = max(score_8)

        values = []

        values.append(min_score_1)
        values.append(max_score_1)
        values.append(min_score_2)
        values.append(max_score_2)
        values.append(min_score_3)
        values.append(max_score_3)
        values.append(min_score_4)
        values.append(max_score_4)
        values.append(min_score_5)
        values.append(max_score_5)
        values.append(min_score_6)
        values.append(max_score_6)
        values.append(min_score_7)
        values.append(max_score_7)
        values.append(min_score_8)
        values.append(max_score_8)
        connection = sql.connect('EclipseBugReports.db')
        query = 'INSERT into table5 VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
        if connection.execute(query, values) is None:
            print 'Db connection none'
        connection.commit()
        connection.close()
    else:
        pass


'''
https://bugs.eclipse.org/bugs/buglist.cgi?bug_status=CLOSED&classification=Eclipse&component=IDE&product=Platform&query_format=advanced&resolution=FIXED
https://bugs.eclipse.org/bugs/buglist.cgi?bug_status=CLOSED&classification=Eclipse&component=CVS&component=Debug&component=IDE&product=Platform&query_format=advanced&resolution=FIXED
'''

'''
<bug_id>307163</bug_id>

        <creation_ts>2010-03-26 05:14:00 -0400</creation_ts>
        <short_desc>DBCS3.6: Resource Filter UI didn't restore grouped filters</short_desc>
        <delta_ts>2010-04-16 03:58:19 -0400</delta_ts>
        <classification>Eclipse</classification>
        <product>Platform</product>
        <component>IDE</component>
        <version>3.6</version>
        <rep_platform>All</rep_platform>
        <op_sys>All</op_sys>
        <bug_status>CLOSED</bug_status>
        <resolution>FIXED</resolution>
        <priority>P2</priority>
        <bug_severity>major</bug_severity>
        <bug_report_text>
'''

#https://bugs.eclipse.org/bugs/buglist.cgi?bug_status=CLOSED&classification=Eclipse&component=IDE&component=Resources&product=Platform&query_format=advanced&resolution=FIXED&ctype=csv&human=0
#https://bugs.eclipse.org/bugs/buglist.cgi?bug_status=CLOSED&classification=Eclipse&component=IDE&component=Resources&order=Importance&product=Platform&query_format=advanced&resolution=FIXED