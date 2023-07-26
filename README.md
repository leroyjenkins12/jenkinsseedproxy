## Building an image
```
# Run inside Seed_Autoscale folder
sudo docker image build -t docker/name:tag --no-cache .
# sudo docker image build -t connorbluestein/bgpchain:v0.3 --no-cache .

docker push connorbluestein/bgpchain:v0.3
```

## Building an environment
```
# In examples folder
python3 {setup env file}.py
cd output_{setup env file}
sudo docker-compose build
sudo docker compose up

# After ending emulation, make sure to run:
sudo docker compose down
```

## Client


## Docker information
### Docker.py
Customizes docker container.

create_mongodb_server.sh - script to set up mongo database inside ix100

### Dockerfile
- Ubuntu 20.04 base image
- Pip and apt installs
- Clones Seed_scalable_complete/bgp_smart_contracts

## Algorithm
Algorithm needs to determine trust level of nodes.

Information we have access to:
| asn               | ip         |
|-------------------|------------|
| age               | age        |
| neighbor segments | validation |
| public key        | count      |
| routes            |            |
| route age         |            |

### Points based trust system
Each piece of information has a point value associated. Proxy can determine trust by setting a required number of points.

For example, for age:
- 72h is good
- week is great
- year+ is great

## Administration
database_manager.py provides funcions to manage a mongoDB server.
- check_asn_conflict(collection, asn)
    - Checks if an asn is in the database
- check_prefix_conflict(collection, ip)
    - Checks if a prefix is in the database
- get_asn(collection, ip)
    - Get an asn from an ip
- get_prefixes(collection, asn)
    - Get a prefix from an asn
- register_asn(collection, asn)
    - Add an asn to the database
- register_prefixes(collection, asn, prefixes)
    - Add a list of prefixes to an asn in the database
- remove_asn(collection, asn)
    - Remove an asn entry from the database
- remove_prefix(collection, asn, ip)
    - Remove a prefix entry from the database
- request_contact(collection, ip)
    - Get the contact information from a prefix entry
- register_contact(collection, ip, contact)
    - Write the contact information for a prefix entry

## Proxy
packet_proxy.py sniffs the network for BGP Update packets, strips out asn and prefixes, then checks if they are listed in the database.

- [x] Sniff packets on port 179
- [ ] Work on any iface
- [x] Strip information
- [x] Connect to mongoDB


