from nltk.tokenize import word_tokenize
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
    docPath = "DEV2"
    # Initialize the index
    index = dict()
    # File "id"
    fid = 1
    # Index id for splitting
    iid = 1
    # How many files to traverse before splitting that index
    splitter = 100
    # Is this line below needed? - Tim
    nltk.download('punkt')
    # Create the indexes folder if not exists
    if not os.path.exists('indexes'):
        os.makedirs('indexes')
    # Remove all contents in the indexes folder for each fresh run
    for f in os.listdir('indexes'):
        os.remove(os.path.join('indexes', f))
    # CHANGE os.walk later as it does not guarantee order (but might not matter for part 1)!
    for root, dirs, files in os.walk(docPath):
        for page in files:
            with open(os.path.join(root, page)) as json_file:
                data = json.load(json_file)
            test_file_contents = data["content"]
            raw_text = BeautifulSoup(test_file_contents, 'html.parser').get_text()
            tokens = word_tokenize(raw_text)
            clean_tokens = [t for t in tokens if re.match(r'[^\W\d]*$', t)]
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
                # Clearing the dictionary should certainly clear the memory, right?
                index.clear()
            # Increment file id after current file is done
            fid += 1
    # The last batch might not reach 100 files, so if the index is not empty, dump another file
    if len(index) != 0:
        with open("indexes/index" + str(iid) + ".json", "w") as save_file:
            json.dump(index, save_file)