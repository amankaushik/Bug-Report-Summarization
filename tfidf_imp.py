#__author__ = 'chanakya'
#-*- coding: utf-8 -*-

'''
#from __future__ import division, unicode_literals
import math
from text.blob import TextBlob as tb
from decimal import Decimal


def tf(word, blob):
    return blob.words.count(word) / len(blob.words)


def n_containing(word, bloblist):
    return sum(1 for blob in bloblist if word in blob)


def idf(word, bloblist):
    return float(Decimal(len(bloblist) / (1 + n_containing(word, bloblist))).ln())



def tfidf(word, blob, bloblist):
    return tf(word, blob) * idf(word, bloblist)

'''
'''
>>> from math import log
>>> from decimal import Decimal

>>> d = Decimal('1E-1024')
>>> log(d)
Traceback (most recent call last):
File "<stdin>", line 1, in <module>
ValueError: math domain error
>>> d.ln()
Decimal('-2357.847135225902780434423250')
'''

import re
import nltk
from nltk.tokenize import RegexpTokenizer

import math


stopwords = nltk.corpus.stopwords.words('portuguese')
tokenizer = RegexpTokenizer("[\w’]+", flags=re.UNICODE)


def freq(word, doc):
    return doc.count(word)


def word_count(doc):
    return len(doc)


def tf(word, doc):
    return (freq(word, doc) / float(word_count(doc)))


def num_docs_containing(word, list_of_docs):
    count = 0
    for document in list_of_docs:
        if freq(word, document) > 0:
            count += 1
    return 1 + count


def idf(word, list_of_docs):
    return math.log(len(list_of_docs) /
            float(num_docs_containing(word, list_of_docs)))


def tf_idf(word, doc, list_of_docs):
    return (tf(word, doc) * idf(word, list_of_docs))

#Compute the frequency for each term.
