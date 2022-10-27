# Install wazuh-agent
Invoke-WebRequest -Uri https://packages.wazuh.com/4.x/windows/wazuh-agent-4.3.8-1.msi -OutFile ${env:tmp}\wazuh-agent-4.3.8.msi; msiexec.exe /i ${env:tmp}\wazuh-agent-4.3.8.msi /q WAZUH_MANAGER='192.168.1.153' WAZUH_REGISTRATION_SERVER='192.168.1.151' WAZUH_REGISTRATION_PASSWORD='password' WAZUH_AGENT_GROUP='default'

#Install chocolatey and nano
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
SET PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin
choco install nano -y

# Copy ossec.conf to specific location
cp .\ossec.conf "C:\Program Files (x86)\ossec-agent\"
cp .\local_internal_options.conf "C:\Program Files (x86)\ossec-agent\"
cp .\script.bat "C:\Program Files (x86)\ossec-agent\active-response\bin\"

# Install Sysmon
.\Sysmon.exe -accepteula -i sysmonconfig.xml

# Start Wazuh Agent
NET START WazuhSvc
 
