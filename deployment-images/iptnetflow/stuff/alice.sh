#!/usr/bin/env bash
ip route add 10.0.20.0/24 via 10.0.10.2 dev eth0
ping 10.0.20.3
