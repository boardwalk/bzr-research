#!/usr/bin/nft -f
add rule nat postrouting ip daddr 74.201.96.00/20 snat 10.0.1.17
