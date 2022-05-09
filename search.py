import os
import json

# Steps:
# 1. Search for EACH search term from the inverted index
# 2. Fetch the documents for each search term
# 3. Find intersection between the retrieved sets of documents

INDEX_PATH = 'indexes/index1.json'

with open(INDEX_PATH) as f:
    index = json.load(f)

# Array containing each word of the query
queries = list(input("Search Query: ").split())

docs = list()

# For each individual word, find the entry in the index, should implement boolean logic here too.
for query in queries:
    pass