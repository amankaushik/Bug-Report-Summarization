#__author__ = 'chanakya'

# One  document at a time

from __future__ import division
from database import DatabaseOperation
from nltk.stem import porter
from math import log
from nltk.cluster import util
#import math
from collections import Counter
from operator import itemgetter

class Features:
    def __init__(self, dbdirec, dbname):
        self.dbdirec = dbdirec
        self.dbname = dbname
        self.id_to_title = {}
        self.id_to_sentences = {}
        self.thematic = {}

    def get_required_resources(self, col_names):
        dobj = DatabaseOperation(self.dbdirec)
        id_to_title = dobj.get_from_database(self.dbname, col_names)  # database name and column names
        self.id_to_title = id_to_title

    def get_score_vector(self, id_to_sentences):
        score = []
        self.id_to_sentences = id_to_sentences
        score_vector = []
        items = id_to_sentences.items()
        bid = items[0][0]
        sentences = items[0][1]
        #---------------------------------
        sentence_len = [len(sentence) for sentence in sentences]
        len_longest_sentence = max(sentence_len)
        #----------------------------------
        low_sen = []
        thematic = {}
        for sen in sentences:
            lower_sentence = [s.lower() for s in sen]
            low_sen.append(lower_sentence)
        for x in low_sen:
            tp = Counter(x)
            for k in tp:
                if k in thematic.keys():
                    thematic[k] += tp[k]
                else:
                    thematic[k] = tp[k]

        sorted_thematic = sorted(thematic.items(), key=itemgetter(1), reverse=True)
        count = 0
        for val in sorted_thematic:
            if count < 5:
                if len(val[0]) > 3:
                    self.thematic[val[0]] = val[1]       # top 5 thematic words in the document
                    count += 1
        #-----------------------------------
        for sentence in sentences:
            score = self.get_all_scores(bid, sentence, len_longest_sentence)
            score_vector.append(score)

        return {bid: score_vector}

    def get_title_score(self, bid, sentence):
        '''
            Title feature: The ratio of the number of words in the
            sentence that occur in the title over the number of words in
        title.
        '''
        score = 0
        title = self.id_to_title[bid].split()
        stem_title = []
        for word in title:
                    stem_title.append(porter.PorterStemmer().stem(word))

        lower_stem_title = [s.lower() for s in stem_title]
        lower_sentence = [s.lower() for s in sentence]

        score = (len(set(lower_stem_title).intersection(set(lower_sentence)))/len(lower_stem_title))
        #print 'Title-set, set-len, len: ', set(lower_stem_title), len(set(lower_stem_title))
        #print 'Sentence-set, set-len: ', set(lower_sentence), len(set(lower_sentence))
        #print 'Sentence-Title-set, set-len: ', set(lower_stem_title).intersection(set(lower_sentence)), len(set(lower_stem_title).intersection(set(lower_sentence)))
        #print 'Score: ', score
        return score

    def get_length_score(self, sentence, l_sentence):
        '''
            Sentence length: The ratio of the number of words
            occurring in the sentence over the number of words occurring
            in the longest sentence of the document.
        '''
        #print 'Sentence: ', sentence, len(sentence)
        #print 'L Sentence: ', l_sentence
        #print 'Ratio: ', len(sentence)/l_sentence
        return len(sentence)/l_sentence

    def get_term_weight_score(self, bid, sentence):
        '''
            Term weight: The ratio of the summary of all terms
            weight in the sentence over the maximum summary of the
            terms weight of the sentence in document.
            TF-ISF
        '''
        all_sentences = self.id_to_sentences[bid]
        N = len(all_sentences)
        avg_val = []
        for term in sentence:
            tf = sentence.count(term)
            n = 0
            for sentence in all_sentences:
                if term in sentence:
                    n += 1
            isf = log(N/n)
            avg_val.append(tf * isf)
        return sum(avg_val)/len(avg_val)

    def get_sentence_position_score(self, bid, sentence):
        '''
            Sentence position: The first 5 sentences in a paragraph
            has a score value of 5/5 for first sentence, the second sentence
            has a score 4/5, and so on.
        '''
        all_sentences = self.id_to_sentences[bid]
        key_sentence = sentence
        total = len(all_sentences)
        i = total
        for sentence in all_sentences:
            if sentence is key_sentence:
                return i/total
            else:
                i -= 1
        pass

    def get_s2s_similarity_score(self, bid, sentence):
        '''
            for a sentence s, the similarity between s and all other sentences is computed by the cosine similarity
            measure. The score of this feature for a sentence is obtained by computing the ratio of the summation of
            sentence similarity of a sentence s with each of the other sentences over the maximum value sentence
            similarity.
        '''
        all_sentences = self.id_to_sentences[bid]
        key_sentence = sentence
        print bid
        print key_sentence
        cosine_sim = []
        for sentence in all_sentences:
            if sentence is not key_sentence:
                v1, v2 = self.buildVector(key_sentence, sentence)
                cosine_sim.append(util.cosine_distance(v1, v2))
        if sum(cosine_sim) != 0.0:
            print 'klkl'
            return sum(cosine_sim)/max(cosine_sim)
        else:
            print 'koko'
            return 0.0

    def buildVector(self, iterable1, iterable2):
        counter1 = Counter(iterable1)
        counter2 = Counter(iterable2)
        all_items = set(counter1.keys()).union( set(counter2.keys()) )
        vector1 = [counter1[k] for k in all_items]
        vector2 = [counter2[k] for k in all_items]
        return vector1, vector2

    def get_proper_noun_score(self, sentence):
        '''
            Proper noun: The ratio of the number of proper nouns
            in sentence over the sentence length.
        '''
        from nltk.tag import pos_tag
        tagged_sent = pos_tag((' '.join(sentence)).split())
        propernouns = [word for word, pos in tagged_sent if pos == 'NNP']
        return len(propernouns)/len(sentence)

    def get_thematic_word_score(self, sentence):
        '''
            Thematic word: The ratio of the number of thematic
            words in the sentence over the maximum summary of thematic
            words of the sentence in document.
        '''
        count = 0
        for word in sentence:
            if word in self.thematic.keys():
                count += 1
        return count


    def get_numerical_data_score(self, sentence):
        '''
            Numerical data: The ratio of the number of numerical
            data in sentence over the sentence length.
        '''
        count = 0
        for word in sentence:
            if word.isdigit():
                count += 1
        return count/len(sentence)

    def get_all_scores(self, bid, sentence, l_sentence):
        score = list()
        score.append(self.get_title_score(bid, sentence))                               # (0-1)
        score.append(self.get_length_score(sentence, l_sentence))                       # (0-1)
        score.append(self.get_term_weight_score(bid, sentence))                         # (0-1)
        score.append(self.get_sentence_position_score(bid, sentence))
        score.append(self.get_s2s_similarity_score(bid, sentence))                      # (0-10)
        score.append(self.get_proper_noun_score(sentence))                              # (0-1)
        score.append(self.get_thematic_word_score(sentence))                            # (0-10)
        score.append(self.get_numerical_data_score(sentence))                           # (0-1)
        return score
