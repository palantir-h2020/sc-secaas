#/bin/bash

#Install wazuh-agent
curl -so wazuh-agent-4.3.8.deb https://packages.wazuh.com/4.x/apt/pool/main/w/wazuh-agent/wazuh-agent_4.3.8-1_amd64.deb && sudo WAZUH_MANAGER='192.168.1.150' WAZUH_REGISTRATION_PASSWORD='password' WAZUH_AGENT_GROUP='default' dpkg -i ./wazuh-agent-4.3.8.deb

#cp ossec.conf
sudo cp ossec.conf /var/ossec/etc/ossec.conf

#audit user activity
sudo apt-get install -y auditd
sudo mkdir /etc/audit/rules.d
sudo cp wazuh.rules /etc/audit/rules.d/

#active response
sudo cp script.sh /var/ossec/active-response/bin/
sudo cp local_internal_options.conf /var/ossec/etc/

#start wazuh agent
sudo systemctl daemon-reload
sudo systemctl enable wazuh-agent
sudo systemctl start wazuh-agent

