#__author__ = 'chanakya'
#-*- coding: utf-8 -*-
#from __future__ import division, unicode_literals
import sqlite3 as sql
from nltk.corpus import stopwords
#import sys
#from nltk.tokenize import sent_tokenize
from nltk.tokenize import punkt
from nltk.stem import porter
#import pprint
#from text.blob import TextBlob as tb
#import tfidf_imp
#from nltk import bigrams, trigrams
#from nltk.tokenize import RegexpTokenizer
#import re



#--------------------------- Term frequency and Inverse document frequency -------------------------------------------

'''
bloblist = []

for id, text in bug_report_text.items():
    doc = tb(text)
    bloblist.append(doc)

for i, blob in enumerate(bloblist):
    #print blob
    print("Top words in document {}".format(i + 1))
    scores = {word: tfidf_imp.tfidf(word, blob, bloblist) for word in blob.words}
    sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    for word, score in sorted_words[:3]:
        print("Word: {}, TF-IDF: {}".format(word, round(score, 5)))

pprint.pprint(scores)
pprint.pprint(sorted_words)
'''
'''
stopwords = stopwords.words('english')
tokenizer = RegexpTokenizer("[\w’]+")
vocabulary = []
docs = {}
all_tips = []
for id, text in bug_report_text.items():
    all_tips.append(text)

for tip in all_tips:
    tokens = tokenizer.tokenize(str(tip))

    bi_tokens = bigrams(tokens)
    tri_tokens = trigrams(tokens)
    tokens = [token.lower() for token in tokens if len(token) > 2]
    tokens = [token for token in tokens if token not in stopwords]

    bi_tokens = [' '.join(token).lower() for token in bi_tokens]
    bi_tokens = [token for token in bi_tokens if token not in stopwords]

    tri_tokens = [' '.join(token).lower() for token in tri_tokens]
    tri_tokens = [token for token in tri_tokens if token not in stopwords]

    final_tokens = []
    final_tokens.extend(tokens)
    final_tokens.extend(bi_tokens)
    final_tokens.extend(tri_tokens)
    docs[tip] = {'freq': {}, 'tf': {}, 'idf': {}, 'tf-idf': {}, 'tokens': []}

    for token in final_tokens:
        #The frequency computed for each tip
        docs[tip]['freq'][token] = tfidf_imp.freq(token, final_tokens)
        #The term-frequency (Normalized Frequency)
        docs[tip]['tf'][token] = tfidf_imp.tf(token, final_tokens)
        docs[tip]['tokens'] = final_tokens

    vocabulary.append(final_tokens)

for doc in docs:
    for token in docs[doc]['tf']:
        #The Inverse-Document-Frequency
        docs[doc]['idf'][token] = tfidf_imp.idf(token, vocabulary)
        #The tf-idf
        docs[doc]['tf-idf'][token] = tfidf_imp.tf_idf(token, docs[doc]['tokens'], vocabulary)

#Now let's find out the most relevant words by tf-idf.
words = {}
for doc in docs:
    for token in docs[doc]['tf-idf']:
        if token not in words:
            words[token] = docs[doc]['tf-idf'][token]
        else:
            if docs[doc]['tf-idf'][token] > words[token]:
                words[token] = docs[doc]['tf-idf'][token]

    print doc
    for token in docs[doc]['tf-idf']:
        print token, docs[doc]['tf-idf'][token]

for item in sorted(words.items(), key=lambda x: x[1], reverse=True):
    print "%f <= %s" % (item[1], item[0])
'''
#----------------------------------------------------------------------------------------


class TextPreprocessing:

    def __init__(self, dbname):
        print 'In init'
        self.database_name = dbname
        self.bug_report_text = {}

    def connect_to_db(self):
        print 'In connect to db'
        connection = None
        try:
            connection = sql.connect(self.database_name)
        except BaseException, ex:
            print str(ex)

        query = 'select bug_id, thetext from table1'
        result = connection.execute(query)
        bug_report_text = {}

        if result is None:
            print 'result none'

        for row in result.fetchall():
            bug_report_text[row[0]] = row[1]

        connection.commit()
        connection.close()

        self.bug_report_text = bug_report_text
        print 'Out Connect to db'
        return bug_report_text

    def noise_reducer(self):
        print 'in Noise Reducer'
        # ------------------------------- NOISE REDUCTION -------------------------------------------------------------

        #--------------------------------- 1. Sentence Segmentation/Tokenization --------------------------------------

        bug_report_text = self.bug_report_text
        sequences = {}  # dictionary of lists of lists('sentences'); keys -> bug id,
        #  values -> segmented bug report text.
        '''
        {'12345':[[this is sentence 1], [this is sentence 2], [this is sentence n]], '6789': [[some information],
                                                          [other information],[more information]]}
        '''
        list_id = []
        for b_id, text in bug_report_text.items():
            list_id.append(id)
            # parses text of bug reports and converts it into a list of sentences stored in variable 'sentences'
            sentences = punkt.PunktSentenceTokenizer().tokenize(text)  # list of lists
            #sent_tokenize(text)+list_id
            # list of 'sentences'
            sequences[b_id] = sentences
            #pprint.pprint(sentences)
        #pprint.pprint(sequences)

        '''
        for items in sequences.items():
            print items, 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' \
                     'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
            break
        '''
        #--------------------------------------------------------------------------------------------------------------

        #-------------------------------- 2. Word Tokenization --------------------------------------------------------

        '''
            takes each sentence list of text report from 'sequences' and tokenizes each sentence in the list of sentences
        '''


        id_to_tokens = {}  # dictionary ; key -> bug id, value -> list of list of word-tokenized sentences of each sentence of the report text
        sequences_2 = sequences
        word_tokens_all_sentences = []
        for b_id, all_sentences in sequences_2.items():
            for each_sentence in all_sentences:
                word_tokens_each_sentence = punkt.PunktWordTokenizer().tokenize(each_sentence)
                word_tokens_all_sentences.append(word_tokens_each_sentence)
            id_to_tokens[b_id] = word_tokens_all_sentences
            word_tokens_all_sentences = []

        '''
        for items in id_to_tokens.items():
            print items, 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' \
                     'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
            break
        '''
        #--------------------------------------------------------------------------------------------------------------

        #------------------------------------- 3. StopWords Removal ---------------------------------------------------

        stop_words = stopwords.words('english')
        clean_token_list = []
        clean_id_token = {}  # dictionary; key -> bug_id, value -> list of list of stopwords removed word-tokenized sentences of each sentence of the report text
        id_to_tokens_2 = id_to_tokens
        for b_id, token_list in id_to_tokens_2.items():
            for each_token_list in token_list:
                filtered_words = [w for w in each_token_list if not w in stop_words]
                clean_token_list.append(filtered_words)
            clean_id_token[b_id] = clean_token_list
            clean_token_list = []

        '''
        for items in clean_id_token.items():
            print items, 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' \
                         'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
            break
        '''
        #--------------------------------------------------------------------------------------------------------------

        #------------------------------------- 4. Stemming ------------------------------------------------------------

        clean_stem_id_token = {}
        clean_stem_token_list = []
        stemmed_words = []
        clean_id_token_2 = clean_id_token
        for b_id, clean_token_list in clean_id_token_2.items():
            for each_clean_token_list in clean_token_list:
                for word in each_clean_token_list:
                    stemmed_words.append(porter.PorterStemmer().stem(word))
                clean_stem_token_list.append(stemmed_words)
                stemmed_words = []
            clean_stem_id_token[b_id] = clean_stem_token_list
            clean_stem_token_list = []

        '''
        for items in clean_stem_id_token.items():
            print items, 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' \
                         'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
            break
        '''
        #--------------------------------------------------------------------------------------------------------------

        #--------------------------------------- END NOISE REDUCTION --------------------------------------------------

        print 'out noise reducer'
        return clean_stem_id_token