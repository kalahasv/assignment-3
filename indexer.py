from nltk.tokenize import word_tokenize
from bs4 import BeautifulSoup
import nltk
import re

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
    # Initialize the index
    index = dict()
    # File "id"
    fc = 1
    #using one json file as a test
    nltk.download('punkt')
    # The DEV folder is in the same directory as this file so relative paths should be fine
    with open("DEV/aiclub_ics_uci_edu/8ef6d99d9f9264fc84514cdd2e680d35843785310331e1db4bbd06dd2b8eda9b.json") as json_file:
        data = json.load(json_file)

    test_file_contents = data["content"]
    raw_text = BeautifulSoup(test_file_contents, 'html.parser').get_text()
    tokens = word_tokenize(raw_text)
    clean_tokens = [t for t in tokens if re.match(r'[^\W\d]*$', t)]
    # Update the inverted index with the tokens
    for t in clean_tokens:
        # Can probably use defaultdict to skip conditional checks?
        if t in index:
            index[t]["locations"].append(fc)
            index[t]["frequency"] += 1
        else:
            index[t] = {
                "locations": [fc],
                "frequency": 1
            }
    with open("index.json", "w") as save_file:
        json.dump(index, save_file)