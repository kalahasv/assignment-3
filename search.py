import os
import json
from posixpath import splitext
from nltk.stem.porter import *
from urllib.parse import urlparse
from pprint import pprint
import time
from bs4 import BeautifulSoup


INDEX_PATH = 'indexes/index1.json'
URL_PATH = 'pathmap.json'
COLLECTION_PATH = 'collection_map.json'

with open(INDEX_PATH) as f:
    index = json.load(f)

with open(URL_PATH) as f:
    urlpath = json.load(f)

with open(COLLECTION_PATH) as f:
    cpath =  json.load(f)


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
        with open(urlpath[i[0]]) as f:
            data = json.load(f)
        extension = splitext(urlparse(data["url"]).path)[1]
        if extension not in ["txt"]:
            urls.append([data["url"], i[1], urlpath[i[0]]])
    return urls

# Create the list of documents to find intersections from
def buildDocList(inputs: list) -> list:
    docs_list = []
    stemmer = PorterStemmer()
    # For each individual word, find the entry in the index, should implement boolean logic here too.
    
    for query in inputs:
        docs = [] # [ [key,value] ]
    # print("Current query: ",query)
        stemmed = stemmer.stem(query)
        #print("Current query, stemmed: ",stemmed)
        #pprint(index.keys())

        if stemmed in index: #if the search is valid 
            
        # Append this query word's locations to the big list of documents
            for k in index[stemmed]['locations']:
                #print("Key: ", k ,  "Value: " ,index[stemmed]['locations'][k])
                docs.append([k,index[stemmed]['locations'][k]]) 

            docs_list.append(docs)
            
                        
        else:
            print("This query is not found in the search index") 
            continue
    return docs_list

def getSortedList(l: list) -> list:
    if len(l) > 1:
        while len(l) > 1:
            #print("Greater than 1")
            same = intersection(l.pop(), l.pop())
            l.append(same)

    #filter out so we're only getting the urls of the top 5
    sorted_docs_list = sorted(l[0], key=lambda x : x[1], reverse=True)
    sorted_docs_list = sorted_docs_list[0:5]
    sorted_docs_list = sorted(sorted_docs_list, key = lambda x: x,reverse= False ) #getting them in key order for easy url retreival
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

# Steps:
# 1. Search for EACH search term from the inverted index
# 2. Fetch the documents for each search term
# 3. Find intersection between the retrieved sets of documents

if __name__ == "__main__":

    while True:
        # Array containing each word of the query
        queries = list(input("Search Query: ").split())
        # The timer begins when the query is beginning to be processed
        start = time.time()
        docs_list = buildDocList(queries)
        
        #filter out so we're only getting the urls of the top 5
        sorted_docs_list = getSortedList(docs_list)

        urls_w_freq = find_urls(sorted_docs_list) #returns the format [url,frequency]
        # The URLs have been found so timer stops
        end = time.time()
        urls_w_freq = sorted(urls_w_freq, key = lambda x: x[1], reverse = True)

        urls_wo_freq = []
        for url in urls_w_freq:
        # pprint(url[0])
            urls_wo_freq.append(url[0])

        pprint(urls_wo_freq)
        print("Time elapsed:", (end - start) * 1000, "milliseconds")
        
    
