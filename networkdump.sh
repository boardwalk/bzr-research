#!/bin/sh
#sudo tcpdump -U -i any -w - udp portrange 9000-9013 > packetloss2.pcap
cat packetloss2.pcap | python3 -u networkdump.py

