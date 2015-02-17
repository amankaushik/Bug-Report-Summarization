__author__ = 'chanakya'

import fuzzy.storage.fcl.Reader
import sqlite3 as sql
from nltk.tokenize import punkt
from pprint import pprint

system = fuzzy.storage.fcl.Reader.Reader().load_from_file("fuzzy_system.fcl")

connection = None
try:
    connection = sql.connect('EclipseBugReports.db')
except BaseException, ex:
    print str(ex)

query = 'select bug_id, NFSV from table4'
result = connection.execute(query)
id_to_sentences_score_vector = {}

if result is None:
    print 'result none'

for row in result.fetchall():
    #print 'ROW: ', row[1]
    #row[1]: u'[[0.75, 0.32, 0.7668666902075585, 19.913901323721589, 0.0625, 1, 0.0],
    #  [0.0, 0.2, 0.313549421592915, 20.160724638695015, 0.1, 1, 0.0]]'
    temp = (row[1][1:len(row[1])-1])
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
        temp_list = (temp[opn[i]+1:close[i]]).split(',')
        #print 'Temp List: ', temp_list
        #temp_list: [u'0.75', u' 0.32', u' 0.7668666902075585', u' 19.913901323721589', u' 0.0625', u' 1', u' 0.0']
        temp_list_of_list.append(temp_list)
    id_to_sentences_score_vector[row[0]] = temp_list_of_list
connection.commit()
connection.close()

#print id_to_sentences_score_vector

# preallocate input and output values

my_input = {"TitleScore": 0.0, "LengthScore": 0.0, "TermWeightScore": 0.0,
            "SentencePositionScore": 0.0, "S2SSimilarityScore": 0.0, "ProperNounScore": 0.0,
            "ThematicWordScore": 0.0, "NumericDataScore": 0.0}

#my_input = {"SentenceFeatureScore1": 0.0}
my_output = {'SentenceRank': 0.0}

id_to_sentence_rank = {}
#print 'ID to Score Vector: '
#pprint(id_to_sentences_score_vector)

for key, values in id_to_sentences_score_vector.items():
    #print values
    rank = []

    for value in values:
        #print value
        #print float(value[0])  # temp_list_of_list contains list of strings
        #print ""
        #break
        my_input["TitleScore"] = float(value[0])
        my_input["LengthScore"] = float(value[1])
        my_input["TermWeightScore"] = float(value[2])
        my_input["SentencePositionScore"] = float(value[3])
        my_input["S2SSimilarityScore"] = float(value[4])
        my_input["ProperNounScore"] = float(value[5])
        my_input["ThematicWordScore"] = float(value[6])
        my_input["NumericDataScore"] = float(value[7])
        #print 'Sentence Scores: '
        #print my_input["SentenceFeatureScore1"]
        #print my_input["SentenceFeatureScore2"]
        #print my_input["SentenceFeatureScore3"]
        #print my_input["SentenceFeatureScore4"]
        #print my_input["SentenceFeatureScore5"]
        #print my_input["SentenceFeatureScore6"]
        #print my_input["SentenceFeatureScore7"]
        #print my_input["SentenceFeatureScore8"]
        system.calculate(my_input, my_output)
        #print my_output['SentenceRank']
        rank.append(my_output['SentenceRank'])
    id_to_sentence_rank[key] = rank
    #print id_to_sentence_rank[key]
    #break

#print id_to_sentence_rank

connection = None
try:
    connection = sql.connect('EclipseBugReports.db')
except BaseException, ex:
    print str(ex)

query = 'select bug_id, thetext from table1'
result = connection.execute(query)
id_to_text = {}
for row in result.fetchall():
            id_to_text[row[0]] = row[1]
#print id_to_text

sequences = {}  # dictionary of lists of lists('sentences'); keys -> bug id,
#values -> segmented bug report text.
#
'''
{'12345':[[this is sentence 1], [this is sentence 2], [this is sentence n]], '6789': [[some information],
                                                          [other information],[more information]]}
'''
list_id = []
for b_id, text in id_to_text.items():
    list_id.append(id)
            # parses text of bug reports and converts it into a list of sentences stored in variable 'sentences'
    sentences = punkt.PunktSentenceTokenizer().tokenize(text)  # list of lists
            #sent_tokenize(text)+list_id
            # list of 'sentences'
    sequences[b_id] = sentences
#print sequences

for key, value in id_to_sentence_rank.items():
    f = open('Summary_'+key+'.txt', 'w')
    num_sen = 0
    total_sen = len(value)
    if total_sen < 4:
        #print key
        #print total_sen
        for i in range(total_sen):
            f.write(sequences[key][i])
            f.write("\n")
            #print sequences[key][i]
        #print "x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-" \
        #      "x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-"
        f.close()
    else:
        lim_sen = int(0.3*total_sen)
        #print key
        #print total_sen, lim_sen, num_sen
        for i in range(total_sen):
            if num_sen > lim_sen:
                break
            if 2.0 <= value[i] <= 3.0:
                num_sen += 1
                f.write(sequences[key][i])
                f.write("\n")
                #print num_sen
                #print sequences[key][i]
        k = 0
        #print 'Starting while 1'
        i = 0
        #print '--->>', lim_sen, num_sen
        while num_sen < lim_sen:
            #print 'In while 1'
            while i < total_sen:
                #print 'In for 1'
                if 1.0 <= value[i] < 2.0:
                    #print 'In if 1'
                    num_sen += 1
                    f.write(sequences[key][i])
                    f.write("\n")
                    #print num_sen
                    #print sequences[key][i]
                    i += 1
                    break
                i += 1
            if k >= total_sen:
                break
            k += 1
        k = 0
        i = 0
        #print '===>>', lim_sen, num_sen
        #print 'Starting while 2'
        while num_sen < lim_sen:
            #print 'In while 2'
            while i < total_sen:
                #print 'In for 2'
                if value[i] < 1.0:
                    #print 'In if 2'
                    num_sen += 1
                    f.write(sequences[key][i])
                    f.write("\n")
                    #print num_sen
                    #print sequences[key][i]
                    i += 1
                    break
                i += 1
            if k >= total_sen:
                break
            k += 1
        f.close()
        #print "x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-" \
        #      "x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-x-"

