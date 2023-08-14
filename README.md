## CURRENT INFO
### Image version: karlolson1/mongo:3
### GitHub: https://github.com/leroyjenkins12/jenkinsseedproxy
### Working Example Env: 1to1_20.py
### TODO
- [ ] ensure Autoscale_100/bgp_smart_contracts/src/proxy.py is working as designed 
(filter and strip packets as necessary)
- [ ] points based trust algorithm
- [ ] add data into "Autoscale_100/routingdb.json" to be used by algorithm
- [ ] ensure database is queried by algorithm

### Work Credits
- Based on thesis and GitHub from LTC Karl Olson, US Army, Army Cyber Institute
- Connor Bluestein and John Byman of Virginia Polytechnical Institute, 1st Cohort ACI Interns 2023
- Brendan Coyne of Norwich University, 3rd Cohort ACI Intern 2023
- 2LT Nathaniel Jenkins, US Army, USMA '23, 3.5th Cohort ACI Intern 2023


## Index
- What does successful test look like?
- Building an image
- Building client environment
- Building an environment
- Common Errors and Fixes
- Docker information
- Database
- Algorithm (to be finished)
- Administration (at the moment, not in use)
- Proxy

## Common Errors and Fixes

#### Nothing Changing Between Environment Builds
- If edited Dockerfile: 
    - Save in VSCode
    - Rebuild image, see "Building an image" section of README
    - Rebuild environment, see "Building an environment" section of README
- If edited Docker.py or other non-Dockerfile files:
    - Ensure you Save in VSCode prior to building environment 
    - Rebuild environment, see "Building an environment" section of README
- If on different device than edit was made on:
    - Save on edit computer
    - Open terminal in working directory
    - Type:
        - Git add {edited file name} 
        #For as many files as necessary
        - Git commit -m "_some comment about changes_"
        - Git push #_sends changes to cloud_
    - Open terminal on non-edit computer
    - Type:
        - Git pull #_should ensure local is up-to-date with remote repository's changes_"
#### Image Changes not Updating
- Find Docker.py in Autoscale_100/seedemu/compiler/
- Find 3 instances where image is listed
- Ensure that it matches most up to date image (e.g., karlolson1/mongo:3)
- In terminal, sudo docker pull karlson1/mongo:3 #_updates the docker image being used_
- Rebuild environment, see "Building an environment" section of README

#### Client Environment
- While not required, a "sudo docker compose down" cannot hurt
- If posing issues, restart the client, see "Building client environment" section of README
- You will know if there are issues if you cannot access map at URL
    - "http://127.0.0.1:8080/map.html#"

#### Compose Up Errors
- If error contains words "overlap" or "daemon" (e.g.,
    _Error response from daemon: network {long seed} not found_ OR _failed to create network {network name}: Error response from daemon: Pool overlaps with other one on this address space_)
    - Type "sudo docker network ls"
    - If results pop up you forgot to compose down, potentially in another folder
    - Will say in which output folder you did not "sudo docker compose down"
        - Network ls looks like: "{network seed} {output_1to1_40_network#} bridge local"
            - Notice in the network name section it includes the folder {output_1to1_40.py}
    - Then try to navigate to that folder to "sudo docker compose down"
    - As last resort, type: "sudo docker network prune"
    - Then rebuild environment, see "Building an environment" section of README
- If containers or networks are stuck after "sudo docker compose down" 
    - Try "sudo docker network prune"
    - As last resort try: "sudo systemctl restart docker.service"
    - Do not prune or restart docker.service without trying composing down
        - Errors can be severe if doing too much

## Building an image
```

#Run inside Autoscale_100 folder
#Open development.env and copy the code (export PYTHONPATH="`pwd`:$PYTHONPATH")
#Paste the code into the terminal (in Autoscale_100)
#Run following commands in the same terminal
#You must paste the development.env for every terminal you create otherwise commands will not work

sudo docker build .
sudo docker image ls | less
#Copy and paste most recent seed
sudo docker image tag {seed} karlolson1/mongo:3 --no-cache
sudo docker push karlolson1/mongo:3

```

## Building client environment
```
#This lets the seed emulator function, MUST DO THIS TO VIEW ENVIRONMENT MAP
#Copy/paste development.env in Autoscale_100 folder, then hit enter
cd client
#In client, run commands:
sudo docker compose build
sudo docker compose up

# After ending emulation, make sure to cancel (CTRL+C), then
sudo docker compose down
# Failure to do so may cause errors
```

## Building an environment
```
#Copy/paste development.env in Autoscale_100 folder, then
cd examples
#In examples folder, pick {setup env file} -> (e.g., 1to1_20.py, 2to1_40.py)
#python3 {setup env file} -d ?? allows random percent of containers to have proxy
python3 {setup env file}.py
cd output_{setup env file}
sudo docker compose build
sudo docker compose up
#Access map at URL: "http://127.0.0.1:8080/map.html#"

# After ending emulation, make sure to run:
sudo docker compose down
# Failure to do so will DEFINITELY cause errors
```

## What does successful test look like? 
### The $ represents command line entry, anything before is the working directory
### 2LT Jenkins wrote shell script to do the Terminal 2 START TEST commands
#### _Test Start_
#### Terminal 1 START TEST
```
$ cd Downloads/jenkinsseedproxy/Autoscale_100
Downloads/jenkinsseedproxy/Autoscale_100$ cat development.env
Downloads/jenkinsseedproxy/Autoscale_100$ export PYTHONPATH="`pwd`:$PYTHONPATH"
Downloads/jenkinsseedproxy/Autoscale_100$ cd client
Downloads/jenkinsseedproxy/Autoscale_100/client$ sudo docker compose build
#will scroll through blue commands then prompt will return
Downloads/jenkinsseedproxy/Autoscale_100/client$ sudo docker compose up
#should say "running (2/2)" then have next line of "Attaching to seedemu_client"
#successful if prompt does not return and you have running process
```
#### Terminal 2 START TEST
```
$ cd Downloads/jenkinsseedproxy/Autoscale_100
Downloads/jenkinsseedproxy/Autoscale_100$ cat development.env
Downloads/jenkinsseedproxy/Autoscale_100$ export PYTHONPATH="`pwd`:$PYTHONPATH"
Downloads/jenkinsseedproxy/Autoscale_100$ cd examples
Downloads/jenkinsseedproxy/Autoscale_100/examples$ python3 1to1_20.py -d 50
#scrolls through blue commands, last line will have "image" & "karlolson1/mongo:3"
Downloads/jenkinsseedproxy/Autoscale_100/examples$ cd output_1to1_20/
Downloads/jenkinsseedproxy/Autoscale_100/examples/output_1to1_20$ sudo docker compose build
#scrolls through white and blue commands
#final entry will look like white: "[+] Building 90.1s (16/16) FINISHED"
#then blue commands, prompt returns
Downloads/jenkinsseedproxy/Autoscale_100/examples/output_1to1_20$ sudo docker compose up
#will create networks, containers, then white block of text, then white and colorful text representing the networks, routers, and hosts connecting to each other
#successful if no repeating errors, then there will stop like process is running
#2LT Jenkins has automated MongoDb to start on IX12/host and import routingdb.json
#This means the database can be queried by any device able to rout traffic to IX12

```

#### Terminal 2 FINISH TEST
```
#Press Ctrl+C multiple times
Downloads/jenkinsseedproxy/Autoscale_100/examples/output_1to1_20$ sudo docker compose down
#will remove networks and containers
```
#### _Test Finished_

## Docker information
### Docker.py
- Customizes docker container.
- Found in Autoscale_100/seedemu/compiler/Docker.py

IMPORTANT: Changes to Docker.py require rebuild of just environment

### Dockerfile
- Ubuntu 20.04 base image
- Pip and apt installs
- Clones jenkinsseedproxy/bgp_smart_contracts
- Ensures containers (routers, hosts, networks) have correct software and image

IMPORTANT: Changes to Dockerfile require rebuild of BOTH image and environment

## Database
- JSON Format
    - Learn JSON so it isn't messed up and is possible to query
- Need ASN, IP, and any other relevant info
- Automatically due to shell script is put into IX12 to serve as db for the proxy

## Algorithm (to be finished)
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

## Administration (at the moment, not in use)
database_manager.py provides functions to manage a mongoDB server.
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
#In Autoscale_100/bgp_smart_contracts/src there is a proxy.py file:
- it sniffs the network for BGP Update packets, strips out asn and prefixes, then checks if they are listed in the database.
- This is the correct proxy to edit, all other ones (e.g., proxy.py, packet_proxy.py, etc) are other versions that do not work


