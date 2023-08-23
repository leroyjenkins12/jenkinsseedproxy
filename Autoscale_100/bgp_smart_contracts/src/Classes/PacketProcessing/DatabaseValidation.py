import pymongo
from Utils.Utils import *

client = pymongo.MongoClient('10.3.0.3', 27017)
db = client["bgp_db"]
collection = db["known_bgp"]

def db_validate(segment, txSender):
    ret = collection.find({'containers.labels.net_0_address': segment}, {'containers.labels.asn': 1})
    if ret.count() == 0:
        return validatePrefixResult.prefixNotRegistered
    elif ret == txSender:
        return validatePrefixResult.prefixValid
    else:
        return validatePrefixResult.prefixOwnersDoNotMatch
