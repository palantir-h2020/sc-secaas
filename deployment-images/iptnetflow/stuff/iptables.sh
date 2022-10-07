#!/usr/bin/env bash
iptables -A FORWARD -j NFLOG --nflog-prefix \"forward:\" --nflog-group 1
fprobe -g 10 -d 10 -e 10 -i eth0 10.0.30.3:12345
while :
do
  cat /var/log/iptables.logging
  pause 10
done
