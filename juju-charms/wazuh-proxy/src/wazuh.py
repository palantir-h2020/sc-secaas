#!/usr/bin/env python3

import json
import logging

import requests
from requests.auth import HTTPBasicAuth

requests.packages.urllib3.disable_warnings()

class Wazuh:
    """Wazuh Class."""

    def __init__(self, wazuh_uri: str) -> None:
        """Wazuh Constructor.

        Args:
            wazuh_uri    (str):  wazuh_manager url to send the request
        """
        self.url = wazuh_uri
        self.log = logging.getLogger("wazuh")


    def __auth_token(self):
        """Receive auth token for Wazuh API."""
        try:
            response = requests.get(url=self.url + "/security/user/authenticate", verify=False,
                auth=HTTPBasicAuth('user', 'password'))
            return response.json()["data"]["token"]
        except Exception as e:
            return f"Error: {e}"


    def list_agents(self) -> str:
        """List agents connected to Wazuh.

        Returns:
            status code:request output  (str)
        """
        try:
            token = self.__auth_token()
            headers =  {"Content-Type":"application/json", "Authorization": f"Bearer {token}"}
            r = requests.get(url=self.url + "/agents", verify=False, headers=headers)
            return r.json()
        except Exception as e:
            return f"Error: {e}"


    def active_response(self, action: str, agent_id: str) -> str:
        """List agents connected to Wazuh.

        Args:
            action    (str):  Active-response action to execute
            agent_id  (str):  Agent id where the action is executed

        Returns:
            status code:request output  (str)
        """
        try:
            token = self.__auth_token()
            headers =  {"Content-Type":"application/json", "Authorization": f"Bearer {token}"}
            params = {"agents_list": agent_id}
            data = '{"command": "!' + action + '", "custom": true}'
            r = requests.put(url=self.url + "/active-response", params=params, headers=headers, data=data, verify=False)
            return r.json()
        except Exception as e:
            return f"Error: {e}"
