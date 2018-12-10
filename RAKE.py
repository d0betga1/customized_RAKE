# Phien ban tuy bien thuat toan RAKE - Rapid Automtic Keyword Exraction algorithm
# duoc gioi thieu trong : 
# Rose, S., D. Engel, N. Cramer, and W. Cowley (2010). 
# Automatic keyword extraction from indi-vidual documents.

# Tim hieu chi tiet trong Sach :
#  M. W. Berry and J. Kogan (Eds.), Text Mining: Applications and Theory.unknown: John Wiley and Sons, Ltd.

# Thay doi so voi ban goc:
# ham tach cau tot hon 
# & thay bo stop_words va verbs cua Spacy

import os
import re
import string
import operator
from predefined_words import STOP_WORDS

def is_number(s):
    try:
        float(s) if '.' in s else int(s)
        return True
    except ValueError:
        return False

def get_content(content_file):
    """
    Lay van ban tu file & lam sach
    
        @param file_path : duong dan den file van ban.
        @return : noi dung file theo tung cau (da lam sach).
    """
    cleaned_data = []

    with open(content_file, encoding='utf-8') as file:
        content = file.readlines()
    content = [x.strip() for x in content]

    # lam sach tung cau
    for line in content:
        cleaned_data.append(
            clean(line)
        )
    return cleaned_data

def clean(content):
    """
    Lam sach cau (chi lay cac ki tu: 0-9, a-z va A-Z)

        @param content : cau can lam sach
        @return : cau da lam sach 
    """
    return re.sub(
        r'[^a-zA-Z0-9\s]'
        ,''
        ,content
    )

def load_stop_words(stop_word_file):
    """
    Lay stop_words tu file va tra ve List cac tu do
  
        @param stop_word_file : duong dan den file stop_words.
        @return : list cac stop_words.
    """
    stop_words = []
    for line in open(stop_word_file):
        if line.strip()[0:1] != "#":
            for word in line.split():               # trong truong hop co nhieu tu mot dong 
                stop_words.append(word)
    return stop_words

def separate_words(text, min_word_return_size):
    """
    Ham tra ve List cac tu(word) thoa man dieu kien : len(word) >= min_word_return_size 

        @param text : Doan van ban ma can tach thanh cac tu(word)
        @param min_word_return_size : so luong toi thieu cac ki tu ma tu(word) co (co the noi la len(word))
    """
    splitter = re.compile('[^a-zA-Z0-9_\\+\\-/]')
    words = []
    for single_word in splitter.split(text):
        current_word = single_word.strip().lower()
        #leave numbers in phrase, but don't count as words, since they tend to invalidate scores of their phrases
        if len(current_word) > min_word_return_size and current_word != '' and not is_number(current_word):
            words.append(current_word)
    return words

def split_sentences(text):
    """
    Tach cau, tra ve List cac cau
    
        @param text : doan van ban can tach cau
        @return : List cac cau  
    """
    # sentence_delimiters = re.compile(u'[.!?,;:\t\\\\"\\(\\)\\\'\u2019\u2013]|\\s\\-\\s')      # old
    sentence_delimiters = re.compile(u'[.!?;:\t\\\\"\\(\\)\\\u2019\u2013]|\\s\\-\\s')           # new
    sentences = sentence_delimiters.split(text)
    return sentences

def build_stop_word_regex(stop_word_file_path, option='from_list'):
    if option == 'from_list':
        stop_word_list = STOP_WORDS
        stop_word_regex_list = []
        for word in stop_word_list:
            word_regex = r'\b' + word + r'(?![\w-])'  # added look ahead for hyphen
            stop_word_regex_list.append(word_regex)
        stop_word_pattern = re.compile('|'.join(stop_word_regex_list), re.IGNORECASE)
        return stop_word_pattern
    else:
        stop_word_list = load_stop_words(stop_word_file_path)
        stop_word_regex_list = []
        for word in stop_word_list:
            word_regex = r'\b' + word + r'(?![\w-])'  # added look ahead for hyphen
            stop_word_regex_list.append(word_regex)
        stop_word_pattern = re.compile('|'.join(stop_word_regex_list), re.IGNORECASE)
        return stop_word_pattern

def generate_candidate_keywords(sentence_list, stopword_pattern):
    phrase_list = []
    for s in sentence_list:
        tmp = re.sub(stopword_pattern, '|', s.strip())
        phrases = tmp.split("|")
        for phrase in phrases:
            phrase = phrase.strip().lower()
            if phrase != "":
                phrase_list.append(phrase)
    return phrase_list

def calculate_word_scores(phraseList):
    word_frequency = {}
    word_degree = {}
    for phrase in phraseList:
        word_list = separate_words(phrase, 0)
        word_list_length = len(word_list)
        word_list_degree = word_list_length - 1
        #if word_list_degree > 3: word_list_degree = 3 #exp.
        for word in word_list:
            word_frequency.setdefault(word, 0)
            word_frequency[word] += 1
            word_degree.setdefault(word, 0)
            word_degree[word] += word_list_degree  #orig.
            #word_degree[word] += 1/(word_list_length*1.0) #exp.
    for item in word_frequency:
        word_degree[item] = word_degree[item] + word_frequency[item]

    # Calculate Word scores = deg(w)/frew(w)
    word_score = {}
    for item in word_frequency:
        word_score.setdefault(item, 0)
        word_score[item] = word_degree[item] / (word_frequency[item] * 1.0)  #orig.
    #word_score[item] = word_frequency[item]/(word_degree[item] * 1.0) #exp.
    return word_score

def generate_candidate_keyword_scores(phrase_list, word_score):
    keyword_candidates = {}
    for phrase in phrase_list:
        keyword_candidates.setdefault(phrase, 0)
        word_list = separate_words(phrase, 0)
        candidate_score = 0
        for word in word_list:
            candidate_score += word_score[word]
        keyword_candidates[phrase] = candidate_score
    return keyword_candidates

class Rake(object):
    def __init__(self, stop_words_path=''):
        if stop_words_path:
            if os.path.isfile(stop_words_path):         # neu khong co file stop_words thi tao tu list stop_words mac dinh
                self.stop_words_path = stop_words_path
                self.__stop_words_pattern = build_stop_word_regex(stop_words_path, option='')
            else:
                self.stop_words_path = stop_words_path
                self.__stop_words_pattern = build_stop_word_regex(stop_words_path, option='from_list')
        else:
            self.stop_words_path = stop_words_path
            self.__stop_words_pattern = build_stop_word_regex(stop_words_path, option='from_list')

    def run(self, content_file):
        if content_file:
            if os.path.isfile(content_file):        # neu co param va co ca file thi moi lam
                # sentence_list = split_sentences(text)
                sentence_list = get_content(content_file)
                phrase_list = generate_candidate_keywords(sentence_list, self.__stop_words_pattern)
                word_scores = calculate_word_scores(phrase_list)
                keyword_candidates = generate_candidate_keyword_scores(phrase_list, word_scores)
                sorted_keywords = sorted(keyword_candidates.items(), key=operator.itemgetter(1), reverse=True)

                # chi in ra cum danh tu 3 am tiet tro xuong
                sorted_keywords_cut = [word for word in sorted_keywords if len( word[0].split() ) <= 3]
                return sorted_keywords_cut
            else:
                return []
        else:
            return []


# =================== TEST ===================

# rake = Rake()

# keywords = rake.run('/home/r/Downloads/lab/crowdSearch/input.txt')

# for i in keywords:
#     print(i)

# ============================================