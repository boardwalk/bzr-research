#!/bin/sh
#sudo tcpdump -U -i any -y raw -w - udp portrange 9000-9013 > login.pcap
cat login.pcap | python3 -u networkdump.py
