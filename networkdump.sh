#!/bin/sh
#sudo tcpdump -U -i any -w - udp portrange 9000-9013 > login2.pcap
cat login2.pcap | python3 -u networkdump.py
