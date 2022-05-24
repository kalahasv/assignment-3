import json
import re
from collections import defaultdict
import os

# Call this on a singular index to split it into alphabetical/miscellaneous files
def splitFile(f1: str) -> None:
    # Create the split_indexes folder if not exists
    if not os.path.exists('split_indexes'):
        os.makedirs('split_indexes')
    # Remove all contents in the split_indexes folder for each fresh run
    for f in os.listdir('split_indexes'):
        os.remove(os.path.join('split_indexes', f))
    d = defaultdict(lambda: dict())
    alpha = re.compile("[A-Za-z]")
    with open(os.path.join("indexes",f1)) as f:
        data = json.load(f)
    for k,v in data.items():
        #print(k, v)
        if alpha.search(k[0]):
            d[k[0].lower()].update({k: v})
        else:
            d["misc"].update({k: v})
    for k,v in d.items():
        with open(os.path.join("split_indexes",k + ".json"), "w") as f:
            json.dump(v, f)
