import os
import json
from posixpath import splitext
from nltk.stem.porter import *
from urllib.parse import urlparse
from pprint import pprint


INDEX_PATH = 'indexes/index1.json'
URL_PATH = 'pathmap.json'

with open(INDEX_PATH) as f:
    index = json.load(f)

with open(URL_PATH) as f:
    urlpath = json.load(f)

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
        urls.append(urlpath[i])
    return urls

# Create the list of documents to find intersections from
def buildDocList(inputs: list) -> list:
    docs_list = []
    stemmer = PorterStemmer()
    # For each individual word, find the entry in the index, should implement boolean logic here too.
    
    for query in queries:
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
            print("This query is not found in the search index") # quit if the query isn't in the index
            continue
    return docs_list

# Steps:
# 1. Search for EACH search term from the inverted index
# 2. Fetch the documents for each search term
# 3. Find intersection between the retrieved sets of documents

if __name__ == "__main__":
    while True:
        # Array containing each word of the query
        queries = list(input("Search Query: ").split())

        
        doc_list = buildDocList(queries)
        
        
        # doc_list is not sorted hence the accuracy of intersection would be affected
        # run the intersection function if more than one query word
        if len(docs_list) > 1:
            while len(docs_list) > 1:
                #print("Greater than 1")
                same = intersection(docs_list.pop(), docs_list.pop())
                docs_list.append(same)

            
        


        #filter out so we're only getting the urls of the top 5
        sorted_docs_list = sorted(docs_list[0], key=lambda x : x[1], reverse=True)
    # print(sorted_docs_list)
        sorted_docs_list = sorted_docs_list[0:5]
        sorted_docs_list = sorted(sorted_docs_list, key = lambda x: x,reverse= False ) #getting them in key order for easy url retreival
        #print(sorted_docs_list)


        #urls = []
        #for item in sorted_docs_list:

        urls_w_freq = find_urls(sorted_docs_list) #returns the format [url,frequency]
        urls_w_freq = sorted(urls_w_freq, key = lambda x: x[1], reverse = True)

        urls_wo_freq = []
        for url in urls_w_freq:
        # pprint(url[0])
            urls_wo_freq.append(url[0])

        pprint(urls_wo_freq)
        
    
