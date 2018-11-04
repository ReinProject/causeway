import hashlib
from settings import *
from models import *


def deduplicate():
    import hashlib
    kvs = Kv.query.all()

    # calculate the hash of each document's contents and its owner 
    summary = {}
    for kv in kvs:
        this_hash = hashlib.sha256( (kv.value + kv.owner).encode('utf8') ).hexdigest()
        if this_hash in summary:
            summary[this_hash].append((kv.key, kv.owner))
        else:
            summary[this_hash] = [(kv.key, kv.owner)]

    # build a list of ids that share that same hash
    #for k in summary.keys():
    #    print(str(len(summary[k])), k, summary[k])

    
    for this_hash in summary.keys():
        l = len(summary[this_hash])
        if l > 1:
            print(this_hash, l, summary[this_hash][0])
            for i in range(1, l):
                print("deleting: " + str(i) + "th " + str(summary[this_hash][i]) + " " + this_hash)    
                kv = Kv.query.filter(Kv.key == summary[this_hash][i][0]).delete() 
            db.session.commit()

if __name__ == '__main__':
    deduplicate()
