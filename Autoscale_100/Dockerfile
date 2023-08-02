FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive
RUN echo 'exec zsh' > /root/.bashrc 
RUN apt-get update && apt-get install -y --no-install-recommends curl dnsutils ipcalc iproute2 iputils-ping jq mtr-tiny mongodb nano netcat tcpdump termshark vim-nox zsh && apt-get install -y build-essential python3 python3-pip python3-dev nodejs git && apt-get install -y npm traceroute libnfnetlink-dev libnetfilter-queue-dev && apt-get install iptables sudo -y 
RUN pip3 install --upgrade pip && pip3 install py-solc-x web3 python-dotenv scapy==2.4.5 Pybird pymongo
RUN curl -L https://grml.org/zsh/zshrc > /root/.zshrc && mkdir -p /usr/share/doc/bird2/examples/ && touch /usr/share/doc/bird2/examples/bird.conf && apt-get update && apt-get install --no-install-recommends bird2 && rm -rf /var/lib/apt/lists/*
# Use 4 byte ASNs
RUN sed -i 's/use_2_bytes_asn = True/use_2_bytes_asn = False/g' /usr/local/lib/python3.8/dist-packages/scapy/contrib/bgp.py
RUN npm update -g && npm install -g ganache@7.5.0 && npm install -g npm@8.5.3
#RUN pip3 install --upgrade pip
RUN pip3 install eth-brownie Flask scapy flask-restful && pip3 install eth-utils netfilterqueue netifaces
RUN curl -fsSL https://pgp.mongodb.com/server-6.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg --dearmor && echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
RUN apt-get update && sudo apt-get install -y mongodb-org
#RUN apt-get install -y libnfnetlink-dev libnetfilter-queue-dev
#RUN pip3 install netfilterqueue
#RUN pip3 install netifaces
#RUN apt-get install iptables sudo -y
#RUN echo "hDessddssdssssssdy"
RUN git clone --depth 1 --filter=blob:none -b experiment https://github.com/KarlOlson/Seed_scalable_complete/
WORKDIR /Seed_scalable_complete
RUN git sparse-checkout set bgp_smart_contracts && git branch && mv bgp_smart_contracts ../bgp_smart_contracts 
#RUN git branch
#RUN mv bgp_smart_contracts ../bgp_smart_contracts
WORKDIR / 
COPY CNERT.pdf CNERT.pdf
COPY /test test
COPY /test /test
COPY /CNERT.pdf /CNERT.pdf
RUN python3 /bgp_smart_contracts/src/solc_ver_install.py
