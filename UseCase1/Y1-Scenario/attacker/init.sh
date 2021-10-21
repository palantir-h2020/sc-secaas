#!/bin/bash
# init.sh

# Define a timestamp function
timestamp() {
  date +"%T" # current time
}

echo "Attacker will sleep for 60 seconds"
timestamp
sleep 60
echo "===================================="
timestamp
echo "Starting port scan"
nmap -T4 -A -v 10.1.1.2
echo "===================================="
timestamp
echo "All done. Exit"
