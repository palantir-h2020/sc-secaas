#! /usr/bin/env python3

import logging

import kubernetes.client
from kubernetes import client, config
from kubernetes.stream import stream

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, MaintenanceStatus, BlockedStatus

logger = logging.getLogger(__name__)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class WazuhproxyCharm(CharmBase):
    """Class representing this Operator charm."""

    def __init__(self, *args):
        """Initialize charm and configure states and events to observe."""
        super().__init__(*args)

        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.list_k8s_services_action, self._on_list_k8s_services_action)
        self.framework.observe(self.on.execute_command_action, self._on_execute_command_action)


    def _on_execute_command_action(self, event):
        try:
            logger.info("Execute command function started")
            command = event.params["cmd"]
            name = event.params["name"]
            v1 = self.get_instance
            namespace = self.get_namespace(name, v1)
            self.pod_exec(name, namespace, command, v1)

            event.set_results({
                "output": f"Execute command: Command executed successfully in {name} container"
            })

        except Exception as e:
            event.fail(f"Stop: Snort service stopped failed with the following exception: {e}")


    def _on_list_k8s_services_action(self, event):
        try:
            logger.info("List k8s services function started")
            v1 = self.get_instance
            print("Listing pods with their IPs:")
            ret = v1.list_pod_for_all_namespaces(watch=False)
            for i in ret.items:
                print("%s\t%s\t%s" %
                    (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

            event.set_results({
                "output": f"Start: Snort service started successfully"
            })

        except Exception as e:
            event.fail(f"Stop: Snort service stopped failed with the following exception: {e}")

    def _on_config_changed(self, event):
        self.unit.status = ActiveStatus()


    @property
    def get_instance(self):
        aToken = "Token"
        aConfiguration = client.Configuration()
        aConfiguration.host = "IP"
        aConfiguration.verify_ssl = False
        aConfiguration.api_key = {"authorization": "Bearer " + aToken}
        aApiClient = client.ApiClient(aConfiguration)

        v1 = client.CoreV1Api(aApiClient)
        return v1


    def get_namespace(self, name, api_instance):
        ret = api_instance.list_pod_for_all_namespaces(watch=False)
        for i in ret.items:
            if i.metadata.name == name:
                return i.metadata.namespace


    def pod_exec(self, name, namespace, command, api_instance):
        exec_command = ["/bin/sh", "-c", command]

        resp = stream(api_instance.connect_get_namespaced_pod_exec,
                  name,
                  namespace,
                  command=exec_command,
                  stderr=True, stdin=False,
                  stdout=True, tty=False,
                  _preload_content=False)

        while resp.is_open():
            resp.update(timeout=1)
            if resp.peek_stdout():
                print(f"STDOUT: \n{resp.read_stdout()}")
            if resp.peek_stderr():
                print(f"STDERR: \n{resp.read_stderr()}")

        resp.close()

        if resp.returncode != 0:
            raise Exception("Script failed")


if __name__ == "__main__":
    main(WazuhproxyCharm)
