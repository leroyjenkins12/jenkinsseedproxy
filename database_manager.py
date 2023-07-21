from pymongo import MongoClient

# Administrative Actions

def check_asn_conflict(collection, asn):
    return len(list(collection.find({"asn":asn}))) > 0

def check_prefix_conflict(collection, ip):
    return len(list(collection.find({"prefix/masks.ip":ip}))) > 0

def get_asn(collection, ip):
    data = collection.find({"prefix/masks.ip":ip}, {"_id":0, "asn":1})
    all_asn = [entries["asn"] for entries in data]
    return all_asn

def get_prefixes(collection, asn):
    data = collection.find({"asn":asn}, {"_id":0, "prefix/masks":1})
    all_prefixes = data[0]["prefix/masks"]
    prefixes = [prefix["ip"] for prefix in all_prefixes]
    return prefixes

def register_asn(collection, asn):
    if not check_asn_conflict(collection, asn):
        new_data = {"asn":asn,
                    "public_key": "",
                    "prefix/masks": [],
                    "RPKI": '',
                    "neighbor_segments": { "local_ASN": 0, "remote_ASN": 0, "age": 'mm:dd:yyyy' },
                    'country/city': '',
                    "routes": {"AS_PATH": [], "selection": 'primary/alt', "age": 'mm:dd:yyyy'}
                    }
        collection.insert_one(new_data)
        return True
    else:
        return False

def register_prefixes(collection, asn, prefixes):
    for ip in prefixes:
        if not check_prefix_conflict(collection, ip):
            data = list(collection.find({"asn":asn}))[0]
            new_data = {"ip": ip,
                        "age": '',
                        "validation": '',
                        "contact": []}
            data['prefix/masks'].append(new_data)
            collection.update_one({"asn":asn}, {"$set": {'prefix/masks': data['prefix/masks']}})
            print(ip, "added")
        else:
            print(ip, "not added")

def remove_asn(collection, asn):
    collection.find_one_and_delete({"asn":asn})
    return True

def remove_prefix(collection, asn, ip):
    data = list(collection.find({"asn":asn}, {"_id":0, "prefix/masks":1}))
    ips = data[0]['prefix/masks']
    for entry in ips:
        if entry["ip"] == ip:
            ips.remove(entry)
            collection.update_one({"asn":asn}, {"$set": {'prefix/masks': ips}})
            return True
    return False

def request_contact(collection, ip):
    data = collection.find({"prefix/masks.ip":ip})
    ips = data[0]['prefix/masks']
    for entry in ips:
        if entry["ip"] == ip:
            return entry["contact"]
    return False

def register_contact(collection, ip, contact):
    data = list(collection.find({"prefix/masks.ip":ip}, {"_id":0, "prefix/masks.ip":1}))
    ips = data[0]["prefix/masks"]
    for count in range(len(ips)):
        if ips[count]["ip"] == ip:
            ips[count]["contact"] = contact
            collection.update_one({"prefix/masks.ip":ip}, {"$set": {'prefix/masks': ips}})
            return True
    return False

client = MongoClient('172.24.0.2', 27017, username='root', password='root')
collection = client.data.ROOT

print(register_asn(collection, 888))