from nltk.tokenize import word_tokenize
from bs4 import BeautifulSoup
import nltk
import re

import json






if __name__ == "__main__":
    #using one json file as a test
    nltk.download('punkt')
   
    with open("/Users/vikasnikalahasthi/Desktop/Assignment_3/DEV/aiclub_ics_uci_edu/8ef6d99d9f9264fc84514cdd2e680d35843785310331e1db4bbd06dd2b8eda9b.json") as json_file:
        data = json.load(json_file)

    test_file_contents = data["content"]
    raw_text = BeautifulSoup(test_file_contents, 'html.parser').get_text()
    tokens = word_tokenize(raw_text)
    clean_tokens = [t for t in tokens if re.match(r'[^\W\d]*$', t)]

    print('done')