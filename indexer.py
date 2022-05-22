from os.path import splitext
from urllib.parse import urlparse
from nltk.tokenize import TweetTokenizer
from nltk.tokenize import word_tokenize
from nltk.stem.porter import *
from bs4 import BeautifulSoup
import nltk
import re
import os
import json
from json_merger import mergeFiles
from pprint import pprint
import importlib

try:
    import mysql.connector
except:
    print("MySQL is not installed on this machine")


# BASE structure for inverted index, can add more attributes:
# {
#   "word": {
#       "locations": {
#        doc_id: frequency 
#        }
#   }
# }
# Can maybe add an "importance" value based on what document it is retrieved from
# Might want to break index into chunks so memory does not get depleted; merge all indexes together in the end

# Auxilliary Structure for td-idf:
# {
#   "word" : collection frequency
#      
# }


if __name__ == "__main__":
    try:
        sqlcheck = importlib.util.find_spec("mysql.connector")
    except:
        sqlcheck = False
    # Define MySQL connection credentials
    if sqlcheck:
        sql = mysql.connector.connect(
            host="localhost",
            user="search",
            password="",
            database="search_engine"
        )
        query = sql.cursor()
        query.execute("TRUNCATE TABLE terms")
        sql.commit()
    # Debug variable for debug output
    IS_DEBUG = True
    # Define path
    docPath = "DEV_TEST"
    # Initialize the index dictionary
    index = {} 
    # Maps doc ids to path
    pathMap = {}
    # Maps term to collection freq
    freqMap = {}
    # File "id"
    fid = 1
    # Index id for splitting
    iid = 1
    # How many files to traverse before splitting that index
    #10000
    splitter = 10000
    # Create the indexes folder if not exists
    if not os.path.exists('indexes'):
        os.makedirs('indexes')
    # Remove all contents in the indexes folder for each fresh run
    for f in os.listdir('indexes'):
        os.remove(os.path.join('indexes', f))

    # tracking total number of unique words
    #numWords = 0
    
    for root, dirs, files in os.walk(docPath):
        dirs.sort() #sort dirs so they are in the same order every time
        for page in files:
            pathMap[fid] = os.path.join(root, page)
            with open(os.path.join(root, page)) as json_file:
                data = json.load(json_file)
            extension = splitext(urlparse(data["url"]).path)[1] #gets the extension 
            if(extension != '.txt' and extension != '.php'): #Note: Unclear whether the "parse html" part of the assignment means the content rather than the website type -Vik
                test_file_contents = data["content"]
                raw_text = BeautifulSoup(test_file_contents, 'lxml').get_text()
                if sqlcheck:
                    title = BeautifulSoup(test_file_contents, 'lxml').find("title")
                    if title != None:
                        # This implementation minimizes the amount of SQL queries needed and space needed (checking for duplicates and selecting distinct values)
                        # Can also modify SQL server settings directly to ignore duplicate errors
                        try:
                            query.execute("INSERT INTO terms (content) VALUES (%s)", (str(title.string).encode("UTF-8"),))
                            sql.commit()
                        except:
                            pass
                ttokenizer = TweetTokenizer()
                tokens = ttokenizer.tokenize(raw_text)

                # Experimental Porter Stemmer
                ps = PorterStemmer()
                
                #clean_tokens = [ps.stem(t) for t in tokens if not re.match(r'[^a-zA-Z\d\s]', t)]    # does not remove special characters
                #clean_tokens = [ps.stem(t) for t in tokens if re.match(r'[a-z0-9A-Z]+', t)]
                clean_tokens = [ps.stem(t) for t in tokens if t.isalnum()]
                clean_tokens.sort()
                # Update the inverted index with the tokens
                for t in clean_tokens:
                    # Can probably use defaultdict to skip conditional checks?
                    if t in index:
                        # Sets are not allowed in JSON syntax so we use a list but check for duplicate elements
                        #Update: Changed  the structure to {word:{doc_id:freq}} 
                        if fid not in index[t]["locations"]:
                            index[t]["locations"][fid] = 1
                        else:
                            index[t]["locations"][fid] += 1
                        #index[t]["frequency"] += 1
                    else:
                        
                        index[t] = {
                            "locations": {fid: 1}
                        }
                    
                        
                if IS_DEBUG:
                    pass
                    #    pprint(index)
                # Split so memory doesn't deplete fully
              
                if fid % splitter == 0:
                    if IS_DEBUG:
                        print("Splitting index", iid, "at fid", fid)
                    with open("indexes/index" + str(iid) + ".json", "w") as save_file:
                        json.dump(index, save_file)
                    # Increment index id after dumping one index file
                    iid += 1
                    #numWords += len(index)
                    # Clearing the dictionary should certainly clear the memory, right? y
                    index.clear()
                # Increment file id after current file is done
                fid += 1
    if sqlcheck:
        sql.close()
    # The last batch might not reach (splitter #) files, so if the index is not empty, dump another file
    if len(index) != 0:
        #numWords += len(index)
        with open("indexes/index" + str(iid) + ".json", "w") as save_file:
            json.dump(index, save_file)
    # save the path map
    with open("pathmap.json", "w") as f:
        json.dump(pathMap, f)

    #generate collection map
    #pprint(index)
    for term in index.keys():      
            total_term_freq = len(index[term]["locations"])
            freqMap[term] = total_term_freq

    
    #save the collection map
    with open("collection_map.json","w") as f:
        json.dump(freqMap,f)
    # merge files
    if os.path.exists('indexes'):
        files = [f for f in os.listdir('indexes')]
    for i in range(1, iid):
        mergeFiles(files[0], files[i])

    # index the index
    # structure: {word: [offset, length]}
    index_offsets = {}

    with open(os.path.join("indexes","index1.json")) as f: 
        index = json.load(f)
        # Turn the index into a string matching the json file
        str_index = '{'
        for key, value in index.items():
            # gets offset of word using 
            index_offsets[key] = [len(str_index), 0]
            str_index += f'"{key}": {value}, '
            # gets length of word in the index
            index_offsets[key][1] = len(str_index) - index_offsets[key][0] - 2
        

    # writing report file
    # report 1 
    numDoc = fid
    with open("report.txt", "w") as outfile:
        outfile.write(f"Number of indexed documents:  {str(numDoc)}\n\n")
    
    # report 2
        with open(os.path.join("indexes","index1.json")) as f:    
            index = json.load(f)
            outfile.write(f"Number of unique words:  {str(len(index))}\n\n")
    # report 3
    # total size (in KB) of index on disk (add later)
    # q
    
