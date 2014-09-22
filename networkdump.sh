#!/bin/sh
#sudo tcpdump -U -i any -w - udp portrange 9000-9013 > temp.pcap
cat traveling.pcap | python3 -u networkdump.py

