import os
import json
from nltk.stem.porter import *

def intersection(x: list, y: list) -> list:
    pass

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
        pass
    else:
        print(docs[0])