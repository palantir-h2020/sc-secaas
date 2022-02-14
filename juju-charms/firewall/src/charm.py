#! /usr/bin/env python3

import logging

from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, MaintenanceStatus, BlockedStatus
import subprocess
import os
import pwd
#import iptc

logger = logging.getLogger(__name__)


class IptnetflowCharm(CharmBase):
    """Class representing this Operator charm."""

    def __init__(self, *args):
        """Initialize charm and configure states and events to observe."""
        super().__init__(*args)

        self.framework.observe(self.on.config_changed, self.configure_pod)
        self.framework.observe(self.on.add_rule_action, self._on_add_rule_action)
        self.framework.observe(self.on.delete_rule_action, self._on_delete_rule_action)
        self.framework.observe(self.on.touch_action, self._on_touch_action)

    def _on_touch_action(self, event):
        filename = event.params["filename"]
        try:
            subprocess.run(["touch", filename])
            event.set_results({
                "output": f"File {filename} created successfully"
            })
        except Exception as e:
            event.fail(f"Touch action failed with the following exception: {e}")

    def _on_add_rule_action(self, event):
        """Add rule to Iptables receiving the complete rule as input"""
        rule = event.params["rule"]
        #pwd.getpwuid(os.getuid())[0] #event.params["rule"]
        try:
            #subprocess.run(["iptables", cmd])
            #chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), "INPUT")
            #rule = iptc.Rule()
            #rule.in_interface = "eth+"
            #rule.src = "127.0.0.1/255.0.0.0"
            #rule.protocol = "icmp"
            #target = iptc.Target(rule, "DROP")
            #rule.target = target
            #chain.insert_rule(rule)
            #uid = pwd.getpwnam('root')[2] #instead of index 2 you can use pw_uid Attribute
            #os.seteuid(uid)
            #os.system(rule)
            s = subprocess.check_output("iptables --list --verbose",shell=True,stderr=subprocess.STDOUT)
            event.set_results({
                "output": f"Rule {s} created successfully into Iptables"
            })
        except Exception as e:
            event.fail(f"Add rule action {rule} failed with the following exception: {e}")

    def _on_delete_rule_action(self, event):
        """Delete rule to Iptables receiving the command as input"""
        rule = event.params["rule"]
        try:
            subprocess.run(["iptables", rule])
            event.set_results({
                "output": f"Rule {rule} deleted successfully into Iptables"
            })
        except Exception as e:
            event.fail(f"Delete rule action failed with the following exception: {e}")

    def configure_pod(self, event):
        if not self.unit.is_leader():
            self.unit.status = ActiveStatus()
            return
        self.unit.status = MaintenanceStatus("Applying pod spec")
        containers = [
            {
                "name": self.framework.model.app.name,
                "image": "lopeez97/iptnetflow:latest",
                "ports": [
                    {
                        "name": "squid",
                        "containerPort": 22,
                        "protocol": "TCP",
                    }
                ],
                "command": ["/bin/bash","-ce","tail -f /dev/null",],
            }
        ]

        self.model.pod.set_spec({"version": 3, "containers": containers})

        self.unit.status = ActiveStatus()
        self.app.status = ActiveStatus()



if __name__ == "__main__":
    main(IptnetflowCharm)
