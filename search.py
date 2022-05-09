import os
import json
from nltk.stem.porter import *

# intersection function based on the pseudocode from class notes
def intersection(x: list, y: list) -> list:
    answer = list()
    cur_x_index = 0
    cur_y_index = 0
    while cur_x_index < len(x) and cur_y_index < len(y):
        if x[cur_x_index] == y[cur_y_index]:
            answer.append(x[cur_x_index])
            cur_x_index += 1
            cur_y_index += 1
        elif x[cur_x_index] < y[cur_y_index]:
            cur_x_index += 1
        else:
            cur_y_index += 1
    return answer

# Steps:
# 1. Search for EACH search term from the inverted index
# 2. Fetch the documents for each search term
# 3. Find intersection between the retrieved sets of documents

if __name__ == "__main__":
    INDEX_PATH = 'indexes/index1.json'

    with open(INDEX_PATH) as f:
        index = json.load(f)

    # Array containing each word of the query
    queries = list(input("Search Query: ").split())

    docs = list()
    stemmer = PorterStemmer()
    # For each individual word, find the entry in the index, should implement boolean logic here too.
    for query in queries:
        stemmed = stemmer.stem(query)
        # Append this query word's locations to the big list of documents
        docs.append(index[stemmed]['locations'])

    # run the intersection function if more than one query word
    if len(docs) > 1:
        while len(docs) > 1:
            same = intersection(docs.pop(), docs.pop())
            docs.append(same)
        print(docs[0])
    else:
        print(docs[0])