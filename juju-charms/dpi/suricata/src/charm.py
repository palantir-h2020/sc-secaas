#! /usr/bin/env python3

import logging

from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, MaintenanceStatus, BlockedStatus
import subprocess
import os

logger = logging.getLogger(__name__)


class SnortCharm(CharmBase):
    """Class representing this Operator charm."""

    def __init__(self, *args):
        """Initialize charm and configure states and events to observe."""
        super().__init__(*args)

        self.framework.observe(self.on.config_changed, self.configure_pod)
        self.framework.observe(self.on.add_rule_action, self._on_add_rule_action)
        self.framework.observe(self.on.update_rules_action, self._on_update_rules_action)
        self.framework.observe(self.on.start_service_action, self._on_start_service_action)
        self.framework.observe(self.on.run_action, self._on_run_action)
        self.framework.observe(self.on.touch_action, self._on_touch_action)

    def _on_touch_action(self, event):
        """Create an empty file receiving the path and filename as input"""
        filename = event.params["filename"]
        try:
            subprocess.run(["touch", filename])
            event.set_results({
                "output": f"File {filename} created successfully"
            })
        except Exception as e:
            event.fail(f"Touch action failed with the following exception: {e}")

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

    def _on_add_rule_action(self, event):
        """Add rule to Snort config"""
        pass

    def _on_update_rules_action(self, event):
        """Update default rules to Suricata config"""
        try:
            os.system("suricata-update")
            event.set_results({
                "output": f"Command: suricata-update executed successfully"
            })
        except Exception as e:
            event.fail(f"Command: suricata-update failed with the following exception: {e}")

    def _on_start_service_action(self, event):
        """Start Suricata service"""
        try:
            os.system("service suricata restart")
            event.set_results({
                "output": f"Start: Suricata service started successfully"
            })
        except Exception as e:
            event.fail(f"Start: Suricata service starting failed with the following exception: {e}")

    def configure_pod(self, event):
        if not self.unit.is_leader():
            self.unit.status = ActiveStatus()
            return
        self.unit.status = MaintenanceStatus("Applying pod spec")
        containers = [
            {
                "name": self.framework.model.app.name,
                "image": "lopeez97/suricata:latest",
                "ports": [
                    {
                        "name": "suricata",
                        "containerPort": 22,
                        "protocol": "TCP",
                    }
                ],
                "command": ["/bin/bash","-ce","tail -f /dev/null",],
                "kubernetes": { "securityContext": { "privileged": True}}
            }
        ]

        self.model.pod.set_spec({"version": 3, "containers": containers})

        self.unit.status = ActiveStatus()
        self.app.status = ActiveStatus()



if __name__ == "__main__":
    main(SnortCharm)
