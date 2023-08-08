from __future__ import annotations
from seedemu.core.Emulator import Emulator
from seedemu.core import Node, Network, Compiler
from seedemu.core.enums import NodeRole, NetworkType
from typing import Dict, Generator, List, Set, Tuple
from hashlib import md5
from os import mkdir, chdir
from re import sub
from ipaddress import IPv4Network, IPv4Address
from shutil import copyfile
import re
from Autoscale_100 import testingPython

SEEDEMU_CLIENT_IMAGE='karlolson1/mongo:3'
ETH_SEEDEMU_CLIENT_IMAGE='rawisader/seedemu-eth-client'

DockerCompilerFileTemplates: Dict[str, str] = {}

DockerCompilerFileTemplates['dockerfile'] = """\
ARG DEBIAN_FRONTEND=noninteractive
RUN echo 'exec zsh' > /root/.bashrc
"""
#Tentative attempt for building out automation to db
DockerCompilerFileTemplates['db_host_automater'] = """\
#! /bin/bash
mkdir -p data/db

mongod --quiet --bind_ip 10.12.0.12
"""

DockerCompilerFileTemplates['db_import_automater'] = """\
#! /bin/bash
sleep 5
mongoimport --host=10.12.0.12 --db='bgp_db' --collection='known_bgp' --file=seedproxydbimports/testingMongo.json

"""
DockerCompilerFileTemplates['dbImport'] = """\
git clone https://github.com/leroyjenkins12/jenkinsseedproxy
cd jenkinsseedproxy/Autoscale_100/
python3 testingPython.py
"""

DockerCompilerFileTemplates['start_script'] = """\
#!/bin/bash
{startCommands}
{specialCommands}
echo "ready! run 'docker exec -it $HOSTNAME /bin/zsh' to attach to this node" >&2
for f in /proc/sys/net/ipv4/conf/*/rp_filter; do echo 0 > "$f"; done
tail -f /dev/null
"""

DockerCompilerFileTemplates['testingMongo'] = """\
{
    "entry1": "value1",
    "entry2": "value2",
    "entry3": 3,
    "entry4": true,
    "entry5": {
      "sub_entry1": "sub_value1",
      "sub_entry2": "sub_value2"
    },
    "entry6": ["item1", "item2", "item3"],
    "entry7": null,
    "entry8": {
      "nested_entry1": "nested_value1",
      "nested_entry2": "nested_value2"
    }
  }
  
"""

DockerCompilerFileTemplates['testingPython'] = """\
from pymongo import MongoClient
from random import randint

client = MongoClient()

client = MongoClient("mongodb://10.2.0.118:27017/")

mydatabase = client['bgp_db']

mycollection = mydatabase['known_bgp']

randomEntryStr = "entry" + str(randint(9, 900))
recordToAdd = {
    randomEntryStr: "This worked!"
}

mycollection = mycollection.insert_one(recordToAdd)
"""

DockerCompilerFileTemplates['seedemu_sniffer'] = """\
#!/bin/bash
last_pid=0
while read -sr expr; do {
    [ "$last_pid" != 0 ] && kill $last_pid 2> /dev/null
    [ -z "$expr" ] && continue
    tcpdump -e -i any -nn -p -q "$expr" &
    last_pid=$!
}; done
[ "$last_pid" != 0 ] && kill $last_pid
"""
#Optionally you can add --database.dbPath /ganache to the ganache command to make database...but not recommended.
DockerCompilerFileTemplates['ganache'] = """\
#!/bin/bash
mkdir -p logs
ganache -a 256 -p 8545 -h 10.100.0.100 --deterministic > logs/bgp-$(date +%Y-%m-%d-%H:%M:%S) & 
sleep 5
cd /bgp_smart_contracts/src 
mkdir pcaps
tcpdump -i any -n tcp port 8545 -w pcaps/blockchain-$(date +%Y-%m-%d-%H:%M:%S).pcap -Z root &
tcpdump -i any -n tcp port 179 -w pcaps/bgp-$(date +%Y-%m-%d-%H:%M:%S).pcap -Z root &
python3 scripts/iana-contract-setup.py 0
# python3 compile.py IANA
# sleep 2 
# python3 deploy.py ACCOUNT0 IANA
# sleep 2
#python3 account_script.py 
echo 'Ganache setup ran. Check Logs for details.'
cd ..
cd ..
"""
DockerCompilerFileTemplates['wait_for_it'] = """\
#!/usr/bin/env bash
# Use this script to test if a given TCP host/port are available

WAITFORIT_cmdname=${0##*/}

echoerr() { if [[ $WAITFORIT_QUIET -ne 1 ]]; then echo "$@" 1>&2; fi }

usage()
{
    cat << USAGE >&2
Usage:
    $WAITFORIT_cmdname host:port [-s] [-t timeout] [-- command args]
    -h HOST | --host=HOST       Host or IP under test
    -p PORT | --port=PORT       TCP port under test
                                Alternatively, you specify the host and port as host:port
    -s | --strict               Only execute subcommand if the test succeeds
    -q | --quiet                Don't output any status messages
    -t TIMEOUT | --timeout=TIMEOUT
                                Timeout in seconds, zero for no timeout
    -- COMMAND ARGS             Execute command with args after the test finishes
USAGE
    exit 1
}

wait_for()
{
    if [[ $WAITFORIT_TIMEOUT -gt 0 ]]; then
        echoerr "$WAITFORIT_cmdname: waiting $WAITFORIT_TIMEOUT seconds for $WAITFORIT_HOST:$WAITFORIT_PORT"
    else
        echoerr "$WAITFORIT_cmdname: waiting for $WAITFORIT_HOST:$WAITFORIT_PORT without a timeout"
    fi
    WAITFORIT_start_ts=$(date +%s)
    while :
    do
        if [[ $WAITFORIT_ISBUSY -eq 1 ]]; then
            nc -z $WAITFORIT_HOST $WAITFORIT_PORT
            WAITFORIT_result=$?
        else
            (echo -n > /dev/tcp/$WAITFORIT_HOST/$WAITFORIT_PORT) >/dev/null 2>&1
            WAITFORIT_result=$?
        fi
        if [[ $WAITFORIT_result -eq 0 ]]; then
            WAITFORIT_end_ts=$(date +%s)
            echoerr "$WAITFORIT_cmdname: $WAITFORIT_HOST:$WAITFORIT_PORT is available after $((WAITFORIT_end_ts - WAITFORIT_start_ts)) seconds"
            sleep 20
            break
        fi
        sleep 1
    done
    return $WAITFORIT_result
}

wait_for_wrapper()
{
    # In order to support SIGINT during timeout: http://unix.stackexchange.com/a/57692
    if [[ $WAITFORIT_QUIET -eq 1 ]]; then
        timeout $WAITFORIT_BUSYTIMEFLAG $WAITFORIT_TIMEOUT $0 --quiet --child --host=$WAITFORIT_HOST --port=$WAITFORIT_PORT --timeout=$WAITFORIT_TIMEOUT &
    else
        timeout $WAITFORIT_BUSYTIMEFLAG $WAITFORIT_TIMEOUT $0 --child --host=$WAITFORIT_HOST --port=$WAITFORIT_PORT --timeout=$WAITFORIT_TIMEOUT &
    fi
    WAITFORIT_PID=$!
    trap "kill -INT -$WAITFORIT_PID" INT
    wait $WAITFORIT_PID
    WAITFORIT_RESULT=$?
    if [[ $WAITFORIT_RESULT -ne 0 ]]; then
        echoerr "$WAITFORIT_cmdname: timeout occurred after waiting $WAITFORIT_TIMEOUT seconds for $WAITFORIT_HOST:$WAITFORIT_PORT"
    fi
    return $WAITFORIT_RESULT
}

# process arguments
while [[ $# -gt 0 ]]
do
    case "$1" in
        *:* )
        WAITFORIT_hostport=(${1//:/ })
        WAITFORIT_HOST=${WAITFORIT_hostport[0]}
        WAITFORIT_PORT=${WAITFORIT_hostport[1]}
        shift 1
        ;;
        --child)
        WAITFORIT_CHILD=1
        shift 1
        ;;
        -q | --quiet)
        WAITFORIT_QUIET=1
        shift 1
        ;;
        -s | --strict)
        WAITFORIT_STRICT=1
        shift 1
        ;;
        -h)
        WAITFORIT_HOST="$2"
        if [[ $WAITFORIT_HOST == "" ]]; then break; fi
        shift 2
        ;;
        --host=*)
        WAITFORIT_HOST="${1#*=}"
        shift 1
        ;;
        -p)
        WAITFORIT_PORT="$2"
        if [[ $WAITFORIT_PORT == "" ]]; then break; fi
        shift 2
        ;;
        --port=*)
        WAITFORIT_PORT="${1#*=}"
        shift 1
        ;;
        -t)
        WAITFORIT_TIMEOUT="$2"
        if [[ $WAITFORIT_TIMEOUT == "" ]]; then break; fi
        shift 2
        ;;
        --timeout=*)
        WAITFORIT_TIMEOUT="${1#*=}"
        shift 1
        ;;
        --)
        shift
        WAITFORIT_CLI=("$@")
        break
        ;;
        --help)
        usage
        ;;
        *)
        echoerr "Unknown argument: $1"
        usage
        ;;
    esac
done

if [[ "$WAITFORIT_HOST" == "" || "$WAITFORIT_PORT" == "" ]]; then
    echoerr "Error: you need to provide a host and port to test."
    usage
fi

WAITFORIT_TIMEOUT=${WAITFORIT_TIMEOUT:-15}
WAITFORIT_STRICT=${WAITFORIT_STRICT:-0}
WAITFORIT_CHILD=${WAITFORIT_CHILD:-0}
WAITFORIT_QUIET=${WAITFORIT_QUIET:-0}

# Check to see if timeout is from busybox?
WAITFORIT_TIMEOUT_PATH=$(type -p timeout)
WAITFORIT_TIMEOUT_PATH=$(realpath $WAITFORIT_TIMEOUT_PATH 2>/dev/null || readlink -f $WAITFORIT_TIMEOUT_PATH)

WAITFORIT_BUSYTIMEFLAG=""
if [[ $WAITFORIT_TIMEOUT_PATH =~ "busybox" ]]; then
    WAITFORIT_ISBUSY=1
    # Check if busybox timeout uses -t flag
    # (recent Alpine versions don't support -t anymore)
    if timeout &>/dev/stdout | grep -q -e '-t '; then
        WAITFORIT_BUSYTIMEFLAG="-t"
    fi
else
    WAITFORIT_ISBUSY=0
fi

if [[ $WAITFORIT_CHILD -gt 0 ]]; then
    wait_for
    WAITFORIT_RESULT=$?
    exit $WAITFORIT_RESULT
else
    if [[ $WAITFORIT_TIMEOUT -gt 0 ]]; then
        wait_for_wrapper
        WAITFORIT_RESULT=$?
    else
        wait_for
        WAITFORIT_RESULT=$?
    fi
fi

if [[ $WAITFORIT_CLI != "" ]]; then
    if [[ $WAITFORIT_RESULT -ne 0 && $WAITFORIT_STRICT -eq 1 ]]; then
        echoerr "$WAITFORIT_cmdname: strict mode, refusing to execute subprocess"
        exit $WAITFORIT_RESULT
    fi
    exec "${WAITFORIT_CLI[@]}"
else
    exit $WAITFORIT_RESULT
fi
"""

DockerCompilerFileTemplates['proxy'] = """\
#!/bin/bash
cd /bgp_smart_contracts/src/ 
mkdir -p logs
./wait_for_it.sh 10.100.0.100:8545 -t 25 -- python3 -u proxy.py {} > logs/log.log &
#tail -f logs/log.log
# sleep 20
# python3 /bgp_smart_contracts/src/scripts/path-validation-setup.py {}

mkdir -p pcaps
# tcpdump -i any -n tcp port 179 -w pcaps/run.pcap -Z root &
tcpdump -i any -n -w pcaps/run.pcap -Z root &
echo 'Proxy setup ran. Listening for packets...'
cd ..
cd ..
"""

DockerCompilerFileTemplates['seedemu_worker'] = """\
#!/bin/bash

net() {
    [ "$1" = "status" ] && {
        ip -j link | jq -cr '.[] .operstate' | grep -q UP && echo "up" || echo "down"
        return
    }

    ip -j li | jq -cr '.[] .ifname' | while read -r ifname; do ip link set "$ifname" "$1"; done
}

bgp() {
    cmd="$1"
    peer="$2"
    [ "$cmd" = "bird_peer_down" ] && birdc dis "$2"
    [ "$cmd" = "bird_peer_up" ] && birdc en "$2"
}

while read -sr line; do {
    id="`cut -d ';' -f1 <<< "$line"`"
    cmd="`cut -d ';' -f2 <<< "$line"`"

    output="no such command."

    [ "$cmd" = "net_down" ] && output="`net down 2>&1`"
    [ "$cmd" = "net_up" ] && output="`net up 2>&1`"
    [ "$cmd" = "net_status" ] && output="`net status 2>&1`"
    [ "$cmd" = "bird_list_peer" ] && output="`birdc s p | grep --color=never BGP 2>&1`"

    [[ "$cmd" == "bird_peer_"* ]] && output="`bgp $cmd 2>&1`"

    printf '_BEGIN_RESULT_'
    jq -Mcr --arg id "$id" --arg return_value "$?" --arg output "$output" -n '{id: $id | tonumber, return_value: $return_value | tonumber, output: $output }'
    printf '_END_RESULT_'
}; done
"""

DockerCompilerFileTemplates['replace_address_script'] = '''\
#!/bin/bash
ip -j addr | jq -cr '.[]' | while read -r iface; do {
    ifname="`jq -cr '.ifname' <<< "$iface"`"
    jq -cr '.addr_info[]' <<< "$iface" | while read -r iaddr; do {
        addr="`jq -cr '"\(.local)/\(.prefixlen)"' <<< "$iaddr"`"
        line="`grep "$addr" < /dummy_addr_map.txt`"
        [ -z "$line" ] && continue
        new_addr="`cut -d, -f2 <<< "$line"`"
        ip addr del "$addr" dev "$ifname"
        ip addr add "$new_addr" dev "$ifname"
    }; done
}; done
'''

DockerCompilerFileTemplates['compose'] = """\
version: "3.4"
services:
{dummies}
{services}
networks:
{networks}
"""

DockerCompilerFileTemplates['compose_dummy'] = """\
    {imageDigest}:
        build:
            context: .
            dockerfile: dummies/{imageDigest}
        image: {imageDigest}
"""

DockerCompilerFileTemplates['compose_service'] = """\
    {nodeId}:
        build: ./{nodeId}
        container_name: {nodeName}
        cap_add:
            - ALL
        sysctls:
            - net.ipv4.ip_forward=1
            - net.ipv4.conf.default.rp_filter=0
            - net.ipv4.conf.all.rp_filter=0
        privileged: true
        networks:
{networks}{ports}{volumes}
        labels:
{labelList}
"""

DockerCompilerFileTemplates['compose_label_meta'] = """\
            org.seedsecuritylabs.seedemu.meta.{key}: "{value}"
"""

DockerCompilerFileTemplates['compose_ports'] = """\
        ports:
{portList}
"""
##removed : from after {portList} to fix dangling : in docker-compose file
DockerCompilerFileTemplates['compose_port'] = """\
            - {hostPort}:{nodePort}/{proto}
"""

DockerCompilerFileTemplates['compose_volumes'] = """\
        volumes:
{volumeList}
"""

DockerCompilerFileTemplates['compose_volume'] = """\
            - type: bind
              source: {hostPath}
              target: {nodePath}
"""

DockerCompilerFileTemplates['compose_storage'] = """\
            - {nodePath}
"""

DockerCompilerFileTemplates['compose_service_network'] = """\
            {netId}:
                ipv4_address: {address}
"""

DockerCompilerFileTemplates['compose_network'] = """\
    {netId}:
        driver_opts:
            com.docker.network.driver.mtu: {mtu}
        ipam:
            config:
                - subnet: {prefix}
        labels:
{labelList}
"""

DockerCompilerFileTemplates['seedemu_client'] = """\
    seedemu-client:
        image: {clientImage}
        container_name: seedemu_client
        volumes:
            - /var/run/docker.sock:/var/run/docker.sock
        ports:
            - {clientPort}:8080/tcp
           
"""

DockerCompilerFileTemplates['seedemu-eth-client'] = """\
    seedemu-eth-client:
        image: {ethClientImage}
        container_name: seedemu-eth-client
        volumes:
            - /var/run/docker.sock:/var/run/docker.sock
        ports:
            - {ethClientPort}:3000/tcp
"""

DockerCompilerFileTemplates['zshrc_pre'] = """\
export NOPRECMD=1
alias st=set_title
"""

DockerCompilerFileTemplates['local_image'] = """\
    {imageName}:
        build:
            context: {dirName}
        image: {imageName}
        ports:
            - {ethclientPort}:3000/tcp
"""

class DockerImage(object):
    """!
    @brief The DockerImage class.

    This class repersents a candidate image for docker compiler.
    """

    __software: Set[str]
    __name: str
    __local: bool
    __dirName: str

    def __init__(self, name: str, software: List[str], local: bool = False, dirName: str = None) -> None:
        """!
        @brief create a new docker image.

        @param name name of the image. Can be name of a local image, image on
        dockerhub, or image in private repo.
        @param software set of software pre-installed in the image, so the
        docker compiler can skip them when compiling.
        @param local (optional) set this image as a local image. A local image
        is built ocally instead of pulled from the docker hub. Default to False.
        @param dirName (optional) directory name of the local image (when local
        is True). Default to None. None means use the name of the image.
        """
        super().__init__()

        self.__name = name
        self.__software = set()
        self.__local = local
        self.__dirName = dirName if dirName != None else name

        for soft in software:
            self.__software.add(soft)

    def getName(self) -> str:
        """!
        @brief get the name of this image.

        @returns name.
        """
        return self.__name

    def getSoftware(self) -> Set[str]:
        """!
        @brief get set of software installed on this image.
        
        @return set.
        """
        return self.__software

    def getDirName(self) -> str:
        """!
        @brief returns the directory name of this image.

        @return directory name.
        """
        return self.__dirName
    
    def isLocal(self) -> bool:
        """!
        @brief returns True if this image is local.

        @return True if this image is local.
        """
        return self.__local

DefaultImages: List[DockerImage] = []

DefaultImages.append(DockerImage('karlolson1/mongo:3', []))

network_devices=[]

class Docker(Compiler):
    """!
    @brief The Docker compiler class.

    Docker is one of the compiler driver. It compiles the lab to docker
    containers.
    """

    __services: str
    __networks: str
    __naming_scheme: str
    __self_managed_network: bool
    __dummy_network_pool: Generator[IPv4Network, None, None]

    __client_enabled: bool
    __client_port: int

    __eth_client_enabled: bool
    __eth_client_port: int

    __client_hide_svcnet: bool

    __images: Dict[str, Tuple[DockerImage, int]]
    __forced_image: str
    __disable_images: bool
    _used_images: Set[str]

    def __init__(
        self,
        namingScheme: str = "as{asn}{role}-{displayName}-{primaryIp}",
        selfManagedNetwork: bool = False,
        dummyNetworksPool: str = '10.128.0.0/9',
        dummyNetworksMask: int = 24,
        clientEnabled: bool = False,
        clientPort: int = 8080,
        ethClientEnabled: bool = False,
        ethClientPort: int = 3000,
        clientHideServiceNet: bool = True
    ):
        """!
        @brief Docker compiler constructor.

        @param namingScheme (optional) node naming scheme. Avaliable variables
        are: {asn}, {role} (r - router, h - host, rs - route server), {name},
        {primaryIp} and {displayName}. {displayName} will automaically fall
        back to {name} if 
        Default to as{asn}{role}-{displayName}-{primaryIp}.
        @param selfManagedNetwork (optional) use self-managed network. Enable
        this to manage the network inside containers instead of using docker's
        network management. This works by first assigning "dummy" prefix and
        address to containers, then replace those address with "real" address
        when the containers start. This will allow the use of overlapping
        networks in the emulation and will allow the use of the ".1" address on
        nodes. Note this will break port forwarding (except for service nodes
        like real-world access node and remote access node.) Default to False.
        @param dummyNetworksPool (optional) dummy networks pool. This should not
        overlap with any "real" networks used in the emulation, including
        loopback IP addresses. Default to 10.128.0.0/9.
        @param dummyNetworksMask (optional) mask of dummy networks. Default to
        24.
        @param clientEnabled (optional) set if seedemu client should be enabled.
        Default to False. Note that the seedemu client allows unauthenticated
        access to all nodes, which can potentially allow root access to the
        emulator host. Only enable seedemu in a trusted network.
        @param clientPort (optional) set seedemu client port. Default to 8080.
        @param clientHideServiceNet (optional) hide service network for the
        client map by not adding metadata on the net. Default to True.
        """
        self.__networks = ""
        self.__services = ""
        self.__naming_scheme = namingScheme
        self.__self_managed_network = selfManagedNetwork
        self.__dummy_network_pool = IPv4Network(dummyNetworksPool).subnets(new_prefix = dummyNetworksMask)

        self.__client_enabled = clientEnabled
        self.__client_port = clientPort

        self.__eth_client_enabled = ethClientEnabled
        self.__eth_client_port = ethClientPort

        self.__client_hide_svcnet = clientHideServiceNet

        self.__images = {}
        self.__forced_image = None
        self.__disable_images = False
        self._used_images = set()

        for image in DefaultImages:
            self.addImage(image)

    def getName(self) -> str:
        return "Docker"

    def addImage(self, image: DockerImage, priority: int = 0) -> Docker:
        """!
        @brief add an candidate image to the compiler.

        @param image image to add.
        @param priority (optional) priority of this image. Used when one or more
        images with same number of missing software exist. The one with highest
        priority wins. If two or more images with same priority and same number
        of missing software exist, the one added the last will be used. All
        built-in images has priority of 0. Default to 0.

        @returns self, for chaining api calls.
        """
        assert image.getName() not in self.__images, 'image with name {} already exists.'.format(image.getName())
        self.__images[image.getName()] = (image, priority)

        return self

    def getImages(self) -> List[Tuple[DockerImage, int]]:
        """!
        @brief get list of images configured.

        @returns list of tuple of images and priority.
        """

        return list(self.__images.values())

    def forceImage(self, imageName: str) -> Docker:
        """!
        @brief forces the docker compiler to use a image, identified by the
        imageName. Image with such name must be added to the docker compiler
        with the addImage method, or the docker compiler will fail at compile
        time. Set to None to disable the force behavior.

        @param imageName name of the image.

        @returns self, for chaining api calls.
        """
        self.__forced_image = imageName

        return self

    def disableImages(self, disabled: bool = True) -> Docker:
        """!
        @brief forces the docker compiler to not use any images and build
        everything for starch. Set to False to disable the behavior.

        @paarm disabled (option) disabled image if True. Default to True.

        @returns self, for chaining api calls.
        """
        self.__disable_images = disabled

        return self

    def _groupSoftware(self, emulator: Emulator):
        """!
        @brief Group apt-get install calls to maximize docker cache. 

        @param emulator emulator to load nodes from.
        """

        registry = emulator.getRegistry()
        
        # { [imageName]: { [softName]: [nodeRef] } }
        softGroups: Dict[str, Dict[str, List[Node]]] = {}

        # { [imageName]: useCount }
        groupIter: Dict[str, int] = {}

        for ((scope, type, name), obj) in registry.getAll().items():
            if type != 'rnode' and type != 'hnode' and type != 'snode' and type != 'rs' and type != 'snode': 
                continue

            node: Node = obj

            (img, _) = self._selectImageFor(node)
            imgName = img.getName()

            if not imgName in groupIter:
                groupIter[imgName] = 0

            groupIter[imgName] += 1

            if not imgName in softGroups:
                softGroups[imgName] = {}

            group = softGroups[imgName]

            for soft in node.getSoftware():
                if soft not in group:
                    group[soft] = []
                group[soft].append(node)

        for (key, val) in softGroups.items():
            maxIter = groupIter[key]
            self._log('grouping software for image "{}" - {} references.'.format(key, maxIter))
            step = 1

            for commRequired in range(maxIter, 0, -1):
                currentTier: Set[str] = set()
                currentTierNodes: Set[Node] = set()

                for (soft, nodes) in val.items():
                    if len(nodes) == commRequired:
                        currentTier.add(soft)
                        for node in nodes: currentTierNodes.add(node)
                
                for node in currentTierNodes:
                    if not node.hasAttribute('__soft_install_tiers'):
                        node.setAttribute('__soft_install_tiers', [])

                    node.getAttribute('__soft_install_tiers').append(currentTier)
                

                if len(currentTier) > 0:
                    self._log('the following software has been grouped together in step {}: {} since they are referenced by {} nodes.'.format(step, currentTier, len(currentTierNodes)))
                    step += 1
                
    
    def _selectImageFor(self, node: Node) -> Tuple[DockerImage, Set[str]]:
        """!
        @brief select image for the given node.

        @param node node.

        @returns tuple of selected image and set of missinge software.
        """
        nodeSoft = node.getSoftware()

        if self.__disable_images:
            self._log('disable-imaged configured, using base image.')
            (image, _) = self.__images['karlolson1/mongo:3']
            return (image, nodeSoft - image.getSoftware())

        if self.__forced_image != None:
            assert self.__forced_image in self.__images, 'forced-image configured, but image {} does not exist.'.format(self.__forced_image)

            (image, _) = self.__images[self.__forced_image]

            self._log('force-image configured, using image: {}'.format(image.getName()))

            return (image, nodeSoft - image.getSoftware())
        
        candidates: List[Tuple[DockerImage, int]] = []
        minMissing = len(nodeSoft)

        for (image, prio) in self.__images.values():
            missing = len(nodeSoft - image.getSoftware())

            if missing < minMissing:
                candidates = []
                minMissing = missing

            if missing <= minMissing: 
                candidates.append((image, prio))

        assert len(candidates) > 0, '_electImageFor ended w/ no images?'

        (selected, maxPiro) = candidates[0]

        for (candidate, prio) in candidates:
            if prio >= maxPiro:
                selected = candidate

        return (selected, nodeSoft - selected.getSoftware())


    def _getNetMeta(self, net: Network) -> str: 
        """!
        @brief get net metadata lables.

        @param net net object.

        @returns metadata lables string.
        """

        (scope, type, name) = net.getRegistryInfo()

        labels = ''

        if self.__client_hide_svcnet and scope == 'seedemu' and name == '000_svc':
            return DockerCompilerFileTemplates['compose_label_meta'].format(
                key = 'dummy',
                value = 'dummy label for hidden node/net'
            )

        labels += DockerCompilerFileTemplates['compose_label_meta'].format(
            key = 'type',
            value = 'global' if scope == 'ix' else 'local'
        )

        labels += DockerCompilerFileTemplates['compose_label_meta'].format(
            key = 'scope',
            value = scope
        )
        

        labels += DockerCompilerFileTemplates['compose_label_meta'].format(
            key = 'name',
            value = name
        )

        labels += DockerCompilerFileTemplates['compose_label_meta'].format(
            key = 'prefix',
            value = net.getPrefix()
        )

        if net.getDisplayName() != None:
            labels += DockerCompilerFileTemplates['compose_label_meta'].format(
                key = 'displayname',
                value = net.getDisplayName()
            )
        
        if net.getDescription() != None:
            labels += DockerCompilerFileTemplates['compose_label_meta'].format(
                key = 'description',
                value = net.getDescription()
            )

        return labels

    def _getNodeMeta(self, node: Node) -> str:
        """!
        @brief get node metadata lables.

        @param node node object.

        @returns metadata lables string.
        """
        (scope, type, name) = node.getRegistryInfo()

        labels = ''

        labels += DockerCompilerFileTemplates['compose_label_meta'].format(
            key = 'asn',
            value = node.getAsn()
        )
        
        DockerCompilerFileTemplates['proxy'].format(node.getAsn(), node.getCrossConnects(), node.getAsn())


        labels += DockerCompilerFileTemplates['compose_label_meta'].format(
            key = 'nodename',
            value = name
        )

        if type == 'hnode':
            labels += DockerCompilerFileTemplates['compose_label_meta'].format(
                key = 'role',
                value = 'Host'
            )

        if type == 'rnode':
            labels += DockerCompilerFileTemplates['compose_label_meta'].format(
                key = 'role',
                value = 'Router'
            )

        if type == 'snode':
            labels += DockerCompilerFileTemplates['compose_label_meta'].format(
                key = 'role',
                value = 'Emulator Service Worker'
            )

        if type == 'rs':
            labels += DockerCompilerFileTemplates['compose_label_meta'].format(
                key = 'role',
                value = 'Route Server'
            )

        if node.getDisplayName() != None:
            labels += DockerCompilerFileTemplates['compose_label_meta'].format(
                key = 'displayname',
                value = node.getDisplayName()
            )
        
        if node.getDescription() != None:
            labels += DockerCompilerFileTemplates['compose_label_meta'].format(
                key = 'description',
                value = node.getDescription()
            )

        n = 0
        for iface in node.getInterfaces():
            net = iface.getNet()

            labels += DockerCompilerFileTemplates['compose_label_meta'].format(
                key = 'net.{}.name'.format(n),
                value = net.getName()
            )

            labels += DockerCompilerFileTemplates['compose_label_meta'].format(
                key = 'net.{}.address'.format(n),
                value = '{}/{}'.format(iface.getAddress(), net.getPrefix().prefixlen)
            )

            n += 1

        return labels

    def _nodeRoleToString(self, role: NodeRole):
        """!
        @brief convert node role to prefix string

        @param role node role

        @returns prefix string
        """
        if role == NodeRole.Host: return 'h'
        if role == NodeRole.Router: return 'r'
        if role == NodeRole.RouteServer: return 'rs'
        assert False, 'unknow node role {}'.format(role)

    def _contextToPrefix(self, scope: str, type: str) -> str:
        """!
        @brief Convert context to prefix.

        @param scope scope.
        @param type type.

        @returns prefix string.
        """
        return '{}_{}_'.format(type, scope)

    def _addFile(self, path: str, content: str) -> str:
        """!
        @brief Stage file to local folder and return Dockerfile command.

        @param path path to file. (in container)
        @param content content of the file.

        @returns COPY expression for dockerfile.
        """

        staged_path = md5(path.encode('utf-8')).hexdigest()
        print(content, file=open(staged_path, 'w'))
        return 'COPY {} {}\n'.format(staged_path, path)
    
    def _importFile(self, path: str, hostpath: str) -> str:
        """!
        @brief Stage file to local folder and return Dockerfile command.

        @param path path to file. (in container)
        @param hostpath path to file. (on host)

        @returns COPY expression for dockerfile.
        """

        staged_path = md5(path.encode('utf-8')).hexdigest()
        copyfile(hostpath, staged_path)
        return 'COPY {} {}\n'.format(staged_path, path)

    def _compileNode(self, node: Node) -> str:
        """!
        @brief Compile a single node. Will create folder for node and the
        dockerfile.

        @param node node to compile.

        @returns docker-compose service string.
        """
        (scope, type, _) = node.getRegistryInfo()
        prefix = self._contextToPrefix(scope, type)
        real_nodename = '{}{}'.format(prefix, node.getName())

        node_nets = ''
        dummy_addr_map = ''

        for iface in node.getInterfaces():
            net = iface.getNet()
            (netscope, _, _) = net.getRegistryInfo()
            net_prefix = self._contextToPrefix(netscope, 'net') 
            if net.getType() == NetworkType.Bridge: net_prefix = ''
            real_netname = '{}{}'.format(net_prefix, net.getName())
            address = iface.getAddress()

            if self.__self_managed_network and net.getType() != NetworkType.Bridge:
                d_index: int = net.getAttribute('dummy_prefix_index')
                d_prefix: IPv4Network = net.getAttribute('dummy_prefix')
                d_address: IPv4Address = d_prefix[d_index]

                net.setAttribute('dummy_prefix_index', d_index + 1)

                dummy_addr_map += '{}/{},{}/{}\n'.format(
                    d_address, d_prefix.prefixlen,
                    iface.getAddress(), iface.getNet().getPrefix().prefixlen
                )

                address = d_address
                
                self._log('using self-managed network: using dummy address {}/{} for {}/{} on as{}/{}'.format(
                    d_address, d_prefix.prefixlen, iface.getAddress(), iface.getNet().getPrefix().prefixlen,
                    node.getAsn(), node.getName()
                ))

            node_nets += DockerCompilerFileTemplates['compose_service_network'].format(
                netId = real_netname,
                address = address
            )
        
        _ports = node.getPorts()
        ports = ''
        if len(_ports) > 0:
            lst = ''
            for (h, n, p) in _ports:
                lst += DockerCompilerFileTemplates['compose_port'].format(
                    hostPort = h,
                    nodePort = n,
                    proto = p
                )
            ports = DockerCompilerFileTemplates['compose_ports'].format(
                portList = lst
            )
        
        _volumes = node.getSharedFolders()
        storages = node.getPersistentStorages()
        
        volumes = ''

        if len(_volumes) > 0 or len(storages) > 0:
            lst = ''

            for (nodePath, hostPath) in _volumes.items():
                lst += DockerCompilerFileTemplates['compose_volume'].format(
                    hostPath = hostPath,
                    nodePath = nodePath
                )
            
            for path in storages:
                lst += DockerCompilerFileTemplates['compose_storage'].format(
                    nodePath = path
                )

            volumes = DockerCompilerFileTemplates['compose_volumes'].format(
                volumeList = lst
            )

        dockerfile = DockerCompilerFileTemplates['dockerfile']
        mkdir(real_nodename)
        chdir(real_nodename)

        (image, soft) = self._selectImageFor(node)

	#KO
	#Removed apt updates and included in base build. added pass.
        if not node.hasAttribute('__soft_install_tiers') and len(soft) > 0:
            #dockerfile += 'RUN apt-get update && apt-get install -y --no-install-recommends {}\n'.format(' '.join(sorted(soft)))
            pass
            
        if node.hasAttribute('__soft_install_tiers'):
            softLists: List[List[str]] = node.getAttribute('__soft_install_tiers')
            for softList in softLists:
                #dockerfile += 'RUN apt-get update && apt-get install -y --no-install-recommends {}\n'.format(' '.join(sorted(softList)))
                pass
	
        #dockerfile += 'RUN curl -L https://grml.org/zsh/zshrc > /root/.zshrc\n'
        dockerfile = 'FROM {}\n'.format(md5(image.getName().encode('utf-8')).hexdigest()) + dockerfile
        self._used_images.add(image.getName())

        for cmd in node.getBuildCommands(): dockerfile += 'RUN {}\n'.format(cmd)

        start_commands = ''
        special_commands = ''

        if self.__self_managed_network:
            start_commands += 'chmod +x /replace_address.sh\n'
            start_commands += '/replace_address.sh\n'
            dockerfile += self._addFile('/replace_address.sh', DockerCompilerFileTemplates['replace_address_script'])
            dockerfile += self._addFile('/dummy_addr_map.txt', dummy_addr_map)
            dockerfile += self._addFile('/root/.zshrc.pre', DockerCompilerFileTemplates['zshrc_pre'])
            dockerfile += self._addFile('/ganache.sh', DockerCompilerFileTemplates['ganache'])
            dockerfile += self._addFile('/proxy.sh', DockerCompilerFileTemplates['proxy'])
	
        for (cmd, fork) in node.getStartCommands():
            start_commands += '{}{}\n'.format(cmd, ' &' if fork else '')

        # if node.getName() == "ix101":
        #     if 100 not in network_devices:
        #         network_devices.append(node.getAsn())
        #     else:

        #Add the file using the dockerfile +=
        #         special_commands += '''python3 /bgp_smart_contracts/src/account_script.py '{}' '''.format([node.getAsn()])
        if node.getName() == "ix12":
                dockerfile += self._addFile('db_host_automater.sh', DockerCompilerFileTemplates['db_host_automater'])
                start_commands += 'chmod +x /db_host_automater.sh\n'
                special_commands += '/db_host_automater.sh\n'

        if node.getName() == "router0":
                dockerfile += self._addFile('db_import_automater.sh', DockerCompilerFileTemplates['db_import_automater'])
                dockerfile += self._addFile('testingMongo.json', DockerCompilerFileTemplates['testingMongo'])
                start_commands += 'chmod +x /db_import_automater.sh\n'
                special_commands += '/db_import_automater.sh\n'

        if node.getName() == "ix100":
                dockerfile += self._addFile('/ganache.sh', DockerCompilerFileTemplates['ganache'])
                start_commands += 'chmod +x /ganache.sh\n'
                special_commands += '/ganache.sh\n'
                
                #Appends each topology node to the array to aid auto deployment (of devices in array)
                network_devices.append(node.getAsn())
                
                #Adds the IX's to the BGP node list to deploy blockchain accounts and data (could simplify this).
                #if 101 not in network_devices and 3 in network_devices: # NOTE: this is specific to A20-nano-internet
                    #network_devices.append(101)
                #if 102 not in network_devices and 3 in network_devices: # NOTE: this is specific to A20-nano-internet
                    #network_devices.append(102) 
                #if 103 not in network_devices and 3 in network_devices: # NOTE: this is specific to A20-nano-internet
                    #network_devices.append(103) 
                #if 104 not in network_devices and 3 in network_devices: # NOTE: this is specific to A20-nano-internet
                    #network_devices.append(104) 
                #if 105 not in network_devices and 3 in network_devices: # NOTE: this is specific to A20-nano-internet
                    #network_devices.append(105)                     
                net_asn=list(set(network_devices))
                print (net_asn)
                #adds setup script on blockchain for every participating node
                special_commands += '''python3 /bgp_smart_contracts/src/account_script.py '{}' '''.format(net_asn)

        if node.getName() == "rw":
                dockerfile += self._addFile('/dbImport.sh', DockerCompilerFileTemplates['dbImport'])
                start_commands += 'chmod +x /dbImport.sh\n'
                special_commands += '/dbImport.sh\n'
        #change to this for random proxy deployment and remove 106:  #host_proxy or proxy in real_nodename
        #if 'host_proxy' in real_nodename:

	#this applies EVERY router to participate in blockchain setup. Modify to change to only nodes deploying proxy.
        #elif (("router" in node.getName()) or (re.match("r[0-9]", node.getName()))):
        elif ("proxy" in node.getName()):
                dockerfile += self._addFile('/proxy.sh', DockerCompilerFileTemplates['proxy'].format(node.getAsn(), node.getCrossConnects(), node.getAsn()))
                dockerfile += self._addFile('/bgp_smart_contracts/src/wait_for_it.sh', DockerCompilerFileTemplates['wait_for_it'])
                start_commands += 'chmod +x /proxy.sh\n'
                start_commands += 'chmod +x /bgp_smart_contracts/src/wait_for_it.sh\n'
                special_commands += '/proxy.sh\n'
                network_devices.append(node.getAsn())

        #Importing the pymongo file and running it 
        # dockerfile += self._addFile('testingPython.py', DockerCompilerFileTemplates['testingPython'])
        # special_commands += 'python3 testingPython.py'
        # # special_commands += testingPython.run123()


        dockerfile += self._addFile('/start.sh', DockerCompilerFileTemplates['start_script'].format(
                startCommands = start_commands,
                specialCommands=special_commands
        ))
        dockerfile += self._addFile('/seedemu_sniffer', DockerCompilerFileTemplates['seedemu_sniffer'])
        dockerfile += self._addFile('/seedemu_worker', DockerCompilerFileTemplates['seedemu_worker'])

        #dockerfile += 'RUN apt-get update && apt-get install -y npm build-essential python3 python3-pip python-dev nodejs git\n'
        #dockerfile += 'RUN pip3 install py-solc-x web3 python-dotenv scapy==2.4.4\n'
        #dockerfile += 'RUN npm update -g\n'
        #dockerfile += 'RUN npm install -g ganache\n'
        #dockerfile += 'RUN npm install -g npm@8.5.3\n'
        #dockerfile += 'RUN pip3 install --upgrade pip\n'
        #dockerfile += 'RUN pip3 install eth-brownie Flask scapy flask-restful\n'
        #dockerfile += 'RUN pip3 install eth-utils\n'
        #dockerfile += 'RUN git clone https://github.com/secdev/scapy.git\n'
        #dockerfile += 'WORKDIR /scapy\n'
        #dockerfile += 'RUN python3 setup.py install\n'
        #dockerfile += 'WORKDIR /\n'
        #dockerfile += 'RUN git clone --depth 1 --filter=blob:none --no-checkout https://github.com/KarlOlson/Seed_scalable_complete/\n'
        #dockerfile += 'WORKDIR /Seed_scalable_complete\n'
        #dockerfile += 'RUN git sparse-checkout set bgp_smart_contracts\n'
        #dockerfile += 'RUN mv bgp_smart_contracts ../bgp_smart_contracts\n'
        #dockerfile += 'WORKDIR /\n'
        #dockerfile += 'RUN apt-get install -y libnfnetlink-dev libnetfilter-queue-dev\n'
        #dockerfile += 'RUN pip3 install netfilterqueue\n'
        #dockerfile += 'RUN apt-get install iptables sudo -y\n'
        #dockerfile += 'RUN python3 /bgp_smart_contracts/src/solc_ver_install.py\n'
        dockerfile += 'RUN chmod +x /start.sh\n'
        dockerfile += 'RUN chmod +x /seedemu_sniffer\n'
        dockerfile += 'RUN chmod +x /seedemu_worker\n'


        for file in node.getFiles():
            (path, content) = file.get()
            dockerfile += self._addFile(path, content)

        for (cpath, hpath) in node.getImportedFiles().items():
            dockerfile += self._importFile(cpath, hpath)

        dockerfile += 'CMD ["/start.sh"]\n'
        print(dockerfile, file=open('Dockerfile', 'w'))

        chdir('..')

        name = self.__naming_scheme.format(
            asn = node.getAsn(),
            role = self._nodeRoleToString(node.getRole()),
            name = node.getName(),
            displayName = node.getDisplayName() if node.getDisplayName() != None else node.getName(),
            primaryIp = node.getInterfaces()[0].getAddress()
        )

        name = sub(r'[^a-zA-Z0-9_.-]', '_', name)

        return DockerCompilerFileTemplates['compose_service'].format(
            nodeId = real_nodename,
            nodeName = name,
            networks = node_nets,
            # privileged = 'true' if node.isPrivileged() else 'false',
            ports = ports,
            labelList = self._getNodeMeta(node),
            volumes = volumes
        )

    def _compileNet(self, net: Network) -> str:
        """!
        @brief compile a network.

        @param net net object.

        @returns docker-compose network string.
        """
        (scope, _, _) = net.getRegistryInfo()
        if self.__self_managed_network and net.getType() != NetworkType.Bridge:
            pfx = next(self.__dummy_network_pool)
            net.setAttribute('dummy_prefix', pfx)
            net.setAttribute('dummy_prefix_index', 2)
            self._log('self-managed network: using dummy prefix {}'.format(pfx))

        net_prefix = self._contextToPrefix(scope, 'net')
        if net.getType() == NetworkType.Bridge: net_prefix = ''

        return DockerCompilerFileTemplates['compose_network'].format(
            netId = '{}{}'.format(net_prefix, net.getName()),
            prefix = net.getAttribute('dummy_prefix') if self.__self_managed_network and net.getType() != NetworkType.Bridge else net.getPrefix(),
            mtu = net.getMtu(),
            labelList = self._getNetMeta(net)
        )

    def _makeDummies(self) -> str:
        """!
        @brief create dummy services to get around docker pull limits.
        
        @returns docker-compose service string.
        """
        mkdir('dummies')
        chdir('dummies')

        dummies = ''

        for image in self._used_images:
            self._log('adding dummy service for image {}...'.format(image))

            imageDigest = md5(image.encode('utf-8')).hexdigest()
            
            dummies += DockerCompilerFileTemplates['compose_dummy'].format(
                imageDigest = imageDigest
            )

            dockerfile = 'FROM {}\n'.format(image)
            print(dockerfile, file=open(imageDigest, 'w'))

        chdir('..')

        return dummies

    def _doCompile(self, emulator: Emulator):
        registry = emulator.getRegistry()

        self._groupSoftware(emulator)

        for ((scope, type, name), obj) in registry.getAll().items():

            if type == 'net':
                self._log('creating network: {}/{}...'.format(scope, name))
                self.__networks += self._compileNet(obj)

        for ((scope, type, name), obj) in registry.getAll().items():

            if type == 'rnode':
                self._log('compiling router node {} for as{}...'.format(name, scope))
                self.__services += self._compileNode(obj)

            if type == 'hnode':
                self._log('compiling host node {} for as{}...'.format(name, scope))
                self.__services += self._compileNode(obj)

            if type == 'rs':
                self._log('compiling rs node for {}...'.format(name))
                self.__services += self._compileNode(obj)

            if type == 'snode':
                self._log('compiling service node {}...'.format(name))
                self.__services += self._compileNode(obj)

        if self.__client_enabled:
            self._log('enabling seedemu-client...')

            self.__services += DockerCompilerFileTemplates['seedemu_client'].format(
                clientImage = SEEDEMU_CLIENT_IMAGE,
                clientPort = self.__client_port
            )

        if self.__eth_client_enabled:
            self._log('enabling seedemu-eth-client...')

            self.__services += DockerCompilerFileTemplates['seedemu-eth-client'].format(
                ethClientImage = ETH_SEEDEMU_CLIENT_IMAGE,
                ethClientPort = self.__eth_client_port,
            )

        local_images = ''

        for (image, _) in self.__images.values():
            if image.getName() not in self._used_images or not image.isLocal(): continue
            local_images += DockerCompilerFileTemplates['local_image'].format(
                imageName = image.getName(),
                dirName = image.getDirName()
            )

        self._log('creating docker-compose.yml...'.format(scope, name))
        print(DockerCompilerFileTemplates['compose'].format(
            services = self.__services,
            networks = self.__networks,
            dummies = local_images + self._makeDummies()
        ), file=open('docker-compose.yml', 'w'))
