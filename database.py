__author__ = 'chanakya'

import os
import sqlite3 as sql
import xml.etree.ElementTree as ET


class DatabaseOperation:
    def __init__(self, dbdir):
        self.db_directory = dbdir

    def parse_files_and_populate(self):
        file_name = []
        for file in os.listdir("/home/chanakya/PycharmProjects/Eclipse Bug Reports"):
            if file.endswith(".xml"):
                 file_name.append(str(file))
        print file_name
        connection = None

        list_of_report_dicts = []

        for files in file_name:
            #xml_parse = minidom.parse(files)
            database_columns = ['bug_id', 'creation_ts', 'short_desc', 'delta_ts', 'product', 'component', 'version', 'bug_status', 'resolution', 'priority', 'bug_severity']
            tree = ET.parse(files)
            root = tree.getroot()
            report_to_list = dict()
            report_text = ''
            for ele in root[0].iter():
                #print ele.tag
                if ele.tag in database_columns:
                    report_to_list[str(ele.tag)] = ele.text
                if ele.tag == 'thetext':
                    report_text += ele.text
                    #break
            #temp_str = ''+report_text
            #temp_text = report_text
            #print temp_str, temp_text
            #break

            temp_text = report_text
            print len(temp_text)
            report_to_list['thetext'] = temp_text
            temp_list = report_to_list
            list_of_report_dicts.append(temp_list)
            report_to_list = {}
            report_text = ''
            #print temp_list, temp_text
        #print len(list_of_report_dicts)
        #pprint.pprint(list_of_report_dicts)

        query_str = 'INSERT INTO table1({}) VALUES({})'
        connection = sql.connect('EclipseBugReports.db')
        for val in list_of_report_dicts:
            #print val.keys()
            columns, values = zip(*val.items())
            #print columns, values
            q = query_str.format(",".join(columns),",".join("?"*len(values)))
            #print q
            if connection.execute(q, values) is None:
                print 'connection none'
        connection.commit()
        connection.close()

            #print report_text, "\n-----------------------------------------------------------------------------" \
            #                   "------------------------------------------------------------------------------\n"

    def write_to_database(self, dbname, tname, content):
        connection = sql.connect(dbname)
        query = 'INSERT into '+ tname + '({}) VALUES({})'

        #for val in list(content):
        columns, values = zip(*content.items())
        q = query.format(",".join(columns),",".join("?"*len(values)))
        print q
        if connection.execute(q, values) is None:
            print 'Db connection none'
        connection.close()

    def get_from_database(self, dbname, col_name):
        dbpath = ''
        id_to_title = {}
        if self.db_directory is '':
            dbpath = dbname
        else:
            dbpath = self.db_directory+"/"+dbname
        #print self.db_directory+"/"+dbname
        connection = sql.connect(dbpath)
        query = 'Select ' + ', '.join(col_name) + ' from table1'
        result = connection.execute(query)
        for row in result.fetchall():
            id_to_title[row[0]] = row[1]
        connection.commit()
        connection.close()
        return id_to_title
