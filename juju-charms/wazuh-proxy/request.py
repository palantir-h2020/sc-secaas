import json
import requests
from requests.auth import HTTPBasicAuth

requests.packages.urllib3.disable_warnings()

username = ""
password = ""
auth = HTTPBasicAuth(username, password)
#response = requests.get(url="http://10.101.15.8:55000/security/user/authenticate", verify=False,
#    auth=auth)
response = requests.get(url="https://10.101.15.7:55000/security/user/authenticate", verify=False,
    auth=auth)
print(response.json()["data"]["token"])

token = response.json()["data"]["token"]
headers =  {"Content-Type":"application/json", "Authorization": f"Bearer {token}"}
r = requests.get("https://10.101.15.7:55000/agents", verify=False, headers=headers)

line = {"output": r.json()}

print(line)
