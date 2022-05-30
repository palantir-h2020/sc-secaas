#! /usr/bin/env python3

import logging

from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, MaintenanceStatus, BlockedStatus
import subprocess
import os
logger = logging.getLogger(__name__)


class VPNCharm(CharmBase):
    """Class representing this Operator charm."""

    def __init__(self, *args):
        """Initialize charm and configure states and events to observe."""
        super().__init__(*args)

        self.framework.observe(self.on.config_changed, self.configure_pod)
        self.framework.observe(self.on.run_action, self._on_run_action)
        self.framework.observe(self.on.start_netflow_action, self._on_start_netflow_action)

    def _on_run_action(self, event):
        """Execute command receiving the command as input"""
        cmd = event.params["cmd"]
        try:
            os.system(cmd)
            event.set_results({
                "output": f"Command: {cmd} executed successfully"
            })
        except Exception as e:
            event.fail(f"Command: {cmd} failed with the following exception: {e}")

    def _on_start_netflow_action(self, event):
        """Initial configuration of OpenVPN"""
        pass

    def configure_pod(self, event):
        if not self.unit.is_leader():
            self.unit.status = ActiveStatus()
            return
        self.unit.status = MaintenanceStatus("Applying pod spec")
        containers = [
            {
                "name": self.framework.model.app.name,
                "image": "lopeez97/openvpn:latest",
                "ports": [
                    {
                        "name": "operator",
                        "containerPort": 22,
                        "protocol": "TCP",
                    },
                    {
                        "name": "openvpn",
                        "containerPort": 1914,
                        "protocol": "TCP",
                    }
                ],
                "command": ["/bin/bash","-ce","tail -f /dev/null",],
                "kubernetes": { "securityContext": { "privileged": True}}
            }
        ]

        #kubernetesResources = {"pod": {"hostNetwork": True}}

        self.model.pod.set_spec({"version": 3, "containers": containers}) #, "kubernetesResources": kubernetesResources})

        self.unit.status = ActiveStatus()
        self.app.status = ActiveStatus()



if __name__ == "__main__":
    main(VPNCharm)
