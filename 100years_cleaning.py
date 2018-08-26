#### File Last Updated: 8/21/2018 by Leslie Davis
#### File purpose: Cleaning all text files to create one csv file to read into pandas

# % matplotlib inline
import nltk
from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.collocations import BigramCollocationFinder
import string
import pandas as pd
import glob
import csv

##### Opening each text file, then calls for text cleaning and frequency calculations #########

def process_file(infile, outfile, append = True):
    first_line = []
    with open(infile,'r', encoding = 'utf-8-sig') as file: #opening and closing file, removes header
        first = file.readline().strip('\n').split(";") #strips newline and splits first line by semicolon
        for word in first:
            word = word.lstrip(' ') #strips leading spaces for each item in the first line of text
            first_line.append(word)
        full_text = word_tokenize(file.read().lower())
        tokens = get_clean_tokens(full_text)
        nltk_text = get_nltk_text(full_text) #returns NLTK text object to find the collocations and concordances
        collocation = get_collocations(nltk_text) #finds key-word pairs
    mapping = freq_map(tokens)
    write_words(first_line, mapping, outfile, nltk_text, collocation, append)

############## Removing punctuation and stopwords from text ###########################

def get_clean_tokens(full_text):
    eng_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't", "and", "for", "next", "one", "also", "many", "her", "said", "she"]
    to_remove = eng_words + [',','.',"'","&", '`', "'s", ":","#", "?", "'", "$"]
    cleantokens = [token for token in full_text if token not in to_remove and not token.isdigit() and len(token) > 2] #removing punctuation and digits
    return cleantokens

############### Finding frequencies of words within each source #########################

def freq_map(tokens):
    mapping = {}
    for word in tokens:
        if word.isalpha() and len(word) > 2:
            if word in mapping:
                mapping[word]+=1
            else:
                mapping[word]= 1
    return mapping

########## Writing each line of the csv with words and corresponding data fields #######################

def write_words(first_line, freq_dict, outfile, nltk_text, collocation, append = True):
    mode = 'a'
    if(not append):
        mode = 'w'
    clean_first_line = []
    with open(outfile, mode) as file:
        for item in first_line:
            split_list = item.split(',') #trying to replace semicolons for commas and vice versa for first_line, make it comma separated for csv
            item = ';'.join(split_list)
            clean_first_line.append(item)
        authors, gender, year, date, s_code, org, topic = map(str, (clean_first_line))
        master_count = 0
        for word,count in freq_dict.items():
            master_count += count #finds the total word count for each source
        for word,count in freq_dict.items():
            concordance = get_concordance(nltk_text, word)
            line = ','.join([word, authors, gender, year, date, s_code, org, topic, str(count), str(master_count), str(concordance), str(collocation)]) + '\n'
            file.writelines(line)

########## Storing original version of text for context analysis ########################

def get_nltk_text(all_words):
    to_remove = [',','.',"'","&", '`', "``", "'s", ":","#", "?", "'", "$", "—", "--", "—-",'—', "''"]
    utftokens = [token for token in all_words if token not in to_remove and len(token) > 1] #removing punctuation and digits
    nltk_text = nltk.Text(utftokens) #returns a nltk text object to later find concordances and collocation
    return nltk_text

########## Finding the contexts of each word ############################

def get_concordance(nltk_text, word, left_margin = 10, right_margin = 10):
    index = nltk.ConcordanceIndex(nltk_text.tokens, key = lambda s: s.lower())
    concordance_txt = ([nltk_text.tokens[list(map(lambda x: x-5 if (x-left_margin)>0 else 0,[offset]))[0]:offset+right_margin]
                        for offset in index.offsets(word)])
    output = [''.join([x+' ' for x in con_sub]) for con_sub in concordance_txt]
    outputFormatted = str(output).replace(",", ";") #making sure that concord. arent broken up by ',' in csv
    return outputFormatted

############ Finding key-word pairs in each source #######################

def get_collocations(nltk_text):
    bigram_measures = nltk.collocations.BigramAssocMeasures()
    finder = BigramCollocationFinder.from_words(nltk_text, window_size = 2)
    colls = finder.nbest(bigram_measures.likelihood_ratio, 7)
    collsFormatted = str(colls).replace(",", ";") #making sure that collocations arent broken by ',' in csv
    return collsFormatted

############# Iterating over all txt files in directory ######################
for filename in glob.iglob('*.txt'):
    process_file(filename, 'final.csv')
