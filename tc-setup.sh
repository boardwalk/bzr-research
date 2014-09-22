#!/bin/sh
set -x

# ip link add $DEV type dummy
DEV=dummy0

tc qdisc delete dev $DEV root

tc qdisc add dev $DEV root handle 10: htb default 1
tc class add dev $DEV parent 10: classid 10:1 htb rate 1Gbit
tc class add dev $DEV parent 10: classid 10:2 htb rate 1Gbit
tc qdisc add dev $DEV parent 10:2 handle 12: netem loss 10%

tc filter add dev $DEV parent 10: protocol ip prio 1 u32 \
    match ip protocol 17 0xff \
    match ip src 74.201.90.00/20 \
    match ip sport 9000 0xfff0 \
    flowid 10:2

tc filter add dev $DEV parent 10: protocol ip prio 1 u32 \
    match ip protocol 17 0xff \
    match ip dst 74.201.90.00/20 \
    match ip dport 9000 0xfff0 \
    flowid 10:2

