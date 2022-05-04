from os.path import splitext
from urllib.parse import urlparse
from nltk.tokenize import TweetTokenizer
from nltk.stem.porter import *
from bs4 import BeautifulSoup
import nltk
import re
import os
import json

# BASE structure for inverted index, can add more attributes:
# {
#   "word": {
#       "locations": [],
#       "frequency": integer,
#   }
# }
# Can maybe add an "importance" value based on what document it is retrieved from
# Might want to break index into chunks so memory does not get depleted; merge all indexes together in the end

if __name__ == "__main__":
    # Debug variable for debug output
    IS_DEBUG = True
    # Define path
    docPath = "DEV"
    # Initialize the index
    index = dict()
    # File "id"
    fid = 1
    # Index id for splitting
    iid = 1
    # How many files to traverse before splitting that index
    splitter = 10000
    # Create the indexes folder if not exists
    if not os.path.exists('indexes'):
        os.makedirs('indexes')
    # Remove all contents in the indexes folder for each fresh run
    for f in os.listdir('indexes'):
        os.remove(os.path.join('indexes', f))
    
    for root, dirs, files in os.walk(docPath):
        dirs.sort() #sort dirs so they are in the same order every time
        for page in files:
            
            with open(os.path.join(root, page)) as json_file:
                data = json.load(json_file)
            extension = splitext(urlparse(data["url"]).path)[1] #gets the extension 
            if(extension != '.txt' and extension != '.php'): #Note: Unclear whether the "parse html" part of the assignment means the content rather than the website type -Vik
                test_file_contents = data["content"]
                raw_text = BeautifulSoup(test_file_contents, 'lxml').get_text()
                tokenizer = TweetTokenizer()
                tokens = tokenizer.tokenize(raw_text)
                # Experimental Porter Stemmer
                ps = PorterStemmer()
                
                clean_tokens = [ps.stem(t) for t in tokens if not re.match(r'[^a-zA-Z\d\s]', t)]
                # Update the inverted index with the tokens
                for t in clean_tokens:
                    # Can probably use defaultdict to skip conditional checks?
                    if t in index:
                        # Sets are not allowed in JSON syntax so we use a list but check for duplicate elements
                        if fid not in index[t]["locations"]:
                            index[t]["locations"].append(fid)
                        index[t]["frequency"] += 1
                    else:
                        index[t] = {
                            "locations": [fid],
                            "frequency": 1
                        }
                # Split so memory doesn't deplete fully
              
                if fid % splitter == 0:
                    if IS_DEBUG:
                        print("Splitting index", iid, "at fid", fid)
                    with open("indexes/index" + str(iid) + ".json", "w") as save_file:
                        json.dump(index, save_file)
                    # Increment index id after dumping one index file
                    iid += 1
                    # Clearing the dictionary should certainly clear the memory, right? y
                    index.clear()
                # Increment file id after current file is done
                fid += 1
    # The last batch might not reach (splitter #) files, so if the index is not empty, dump another file
    if len(index) != 0:
        with open("indexes/index" + str(iid) + ".json", "w") as save_file:
            json.dump(index, save_file)
            
    # report
