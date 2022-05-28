import os
import json
from posixpath import splitext
from nltk.stem.porter import *
from urllib.parse import urlparse, urldefrag
from pprint import pprint
import time
from bs4 import BeautifulSoup
import json_splitter
import string
import math


INDEX_PATH = 'indexes/index1.json'
#URL_PATH = 'pathmap.json'
DF_PATH = 'df_map.json'
TF_PATH = 'tf_map.json'

URL = 'urlmap.json'

'''with open(URL_PATH) as f:
    urlpath = json.load(f)'''

with open(DF_PATH) as f:
    dfMap = json.load(f)

with open(TF_PATH) as f:
    tfMap = json.load(f)

with open(URL) as f:
    urlTable = json.load(f)

misc_ind = ""
letter_indexes = {}

#term -> term that's being searched for
#doc -> doc you're searching in 
#freq -> to get the times the term occurs in the doc
def findTdidfWeight(term: string, doc: string, freq: int):

    tf = freq/tfMap[doc]
    idf = dfMap["TOTAL_DOCS"]/(dfMap[term]+1)

    
    weight = tf * (math.log(idf,10))

    return weight
# intersection function based on the pseudocode from class notes
def intersection(x: list, y: list) -> list:
    #print(x)
    #print(y)
    answer = list()
    cur_x_index = 0
    cur_y_index = 0

    while cur_x_index < len(x) and cur_y_index < len(y):
        if x[cur_x_index][0] == y[cur_y_index][0]:
            total_freq = x[cur_x_index][1] + y[cur_y_index][1]
            answer.append([x[cur_x_index][0],total_freq])
            cur_x_index += 1
            cur_y_index += 1
        elif x[cur_x_index][0] < y[cur_y_index][0]:
            cur_x_index += 1
        else:
            cur_y_index += 1
    return answer

# Find the URLs from the mapped path file
def find_urls(index_list) -> list: #returns a list of urls associated with the given fids 
    urls = []
    for i in index_list:
        '''with open(urlpath[i[0]]) as f:
            data = json.load(f)
        extension = splitext(urlparse(data["url"]).path)[1]
        if extension not in ["txt"]:
            urls.append([urldefrag(data["url"])[0], i[1], urlpath[i[0]]])'''
            
      #  urls.append([urlTable[i[0]],i[1]])      # use url lookup table directly
        urls.append(urlTable[i])
    return urls

# Create the list of documents to find intersections from
def buildDocDictionary(inputs: list) -> list:
    docs_list = []
    docs_dict = {}
    stemmer = PorterStemmer()

    # makes sure the variables defined in __main__ can be used here 
    # (had a problem with using misc_ind inside this function)
    global misc_ind 
    global letter_indexes
    # For each individual word, find the entry in the index, should implement boolean logic here too.

    for query in inputs:

        docs = [] # [ [key,value] ]
        #print("Current query: ",query)
        stemmed = stemmer.stem(query)
        #print("Current query, stemmed: ",stemmed)
        #pprint(index.keys())

        first_char = stemmed[0]
       
        #print(first_char)

        # If first character in the word is a letter, find associated word in stemmed file
        if first_char in list(string.ascii_lowercase):
            #letter_indexes[first_char] = json.load(open(os.path.join("split_indexes", first_char + ".json")))
            if (first_char in letter_indexes) and os.path.exists(os.path.join("split_indexes", first_char + ".json")) and (letter_indexes[first_char] == ""):
                #print(first_char)
                letter_indexes[first_char] = json.load(open(os.path.join("split_indexes", first_char + ".json")))
                #print(letter_indexes[first_char])
            stemmed_index = letter_indexes[first_char]
        # Else, find in the miscellaneous file
        else:
            if (misc_ind == "") and os.path.exists(os.path.join("split_indexes", "misc.json")):
                misc_ind = json.load(open(os.path.join("split_indexes", "misc" + ".json")))
            stemmed_index = misc_ind
            
        # If the word is in the file, find the doc ids and the number of appearances
        
        if stemmed in stemmed_index:
           docs_dict[stemmed] =  stemmed_index[stemmed]['locations']

            
           # for key, value in stemmed_index[stemmed]['locations'].items():
            #    docs.append([key, value])
                
            # Append this query word's locations to the big list of documents
            #docs_list.append(docs)   '''

        else:
            print("This query is not found in the search index") # quit if the query isn't in the index
            continue 
    
    
    return docs_dict

def getSortedList(l: list) -> list:
    if len(l) > 1:
        while len(l) > 1:
            #print("Greater than 1")
            same = intersection(l.pop(), l.pop())       # no need to use intersection once implementing td-idf
            l.append(same)
    #filter out so we're only getting the urls of the top 5
    if (len(l) > 0):
        sorted_docs_list = sorted(l[0], key=lambda x : x[1], reverse=True)
        sorted_docs_list = sorted_docs_list[0:5]
        sorted_docs_list = sorted(sorted_docs_list, key = lambda x: x,reverse= False ) #getting them in key order for easy url retreival
    else:
        sorted_docs_list = []
    return sorted_docs_list

def searchEngineData(l: list) -> list:
    d = list()
    for item in l:
        with open(item[2]) as f:
            data = json.load(f)
        title = BeautifulSoup(data["content"], 'lxml').find("title")
        if title == None:
            title = data["url"]
        else:
            title = str(title.string)
        preview = BeautifulSoup(data["content"], 'lxml').get_text()[:250]
        d.append([title, preview, item[0], item[2]])
    return d

def searchInit() -> None:
    alphabet = list(string.ascii_lowercase)
    for letter in alphabet:
        letter_indexes[letter] = ""
    misc_index = ""

# Steps:
# 1. Search for EACH search term from the inverted index
# 2. Fetch the documents for each search term
# 3. Find intersection between the retrieved sets of documents

if __name__ == "__main__":
    #open_split_files()

    # Create empty split indexes
    searchInit()

    while True:    
        # Array containing each word of the query
        queries = list(input("Search Query: ").split())
        # The timer begins when the query is beginning to be processed
        start = time.time()

        docs_dictionary = buildDocDictionary(queries)
        
        print("Document Dictionary:", docs_dictionary)
        #filter out so we're only getting the urls of the top 5

        tdidfDict = {}
        #Dictionary for holding the td-idf scores of each document, total
        # { doc: td-idf }
        #Eventually needs to sort doc-id by value 
        #then need to grab top 5

        #term at a time query processing 
        for term in docs_dictionary:
            #for each term, calculate the partial td-idf in each document it appears in 
            for k,v in docs_dictionary[term].items():
                temp_weight = findTdidfWeight(term,k,v)
                if(k not in tdidfDict):
                    tdidfDict[k] = temp_weight
                else:
                    tdidfDict[k] += temp_weight

        print(tdidfDict)
        sorted_docs_list = sorted(tdidfDict, key=tdidfDict.get, reverse=True)
        sorted_docs_list = sorted_docs_list[0:5]
        print("Sorted Document list:",sorted_docs_list)
     
        
        #sorted_docs_list = getSortedList(docs_dictionary)
        
        urls_found = find_urls(sorted_docs_list) #returns the format [url,frequency]
        # The URLs have been found so timer stops
        end = time.time()

        #urls_w_freq = sorted(urls_w_freq, key = lambda x: x[1], reverse = True)
        
        #print(urls_w_freq)

       # urls_wo_freq = []
        #for url in urls_w_freq:
        # pprint(url[0])
         #   urls_wo_freq.append(url[0])
        print(urls_found)
        #pprint(urls_wo_freq)
        print("Time elapsed:", end - start)
        
        #break
