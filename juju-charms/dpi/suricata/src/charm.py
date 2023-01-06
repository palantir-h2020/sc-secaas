#! /usr/bin/env python3

import logging

from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, MaintenanceStatus, BlockedStatus
import subprocess
import os
import fileinput
import psutil
import json

logger = logging.getLogger(__name__)


class SuricataCharm(CharmBase):
    """Class representing this Operator charm."""

    def __init__(self, *args):
        """Initialize charm and configure states and events to observe."""
        super().__init__(*args)

        self.framework.observe(self.on.config_changed, self.configure_pod)
        self.framework.observe(self.on.add_rule_action, self._on_add_rule_action)
        self.framework.observe(self.on.del_rule_action, self._on_del_rule_action)
        self.framework.observe(self.on.start_service_action, self._on_start_service_action)
        self.framework.observe(self.on.stop_service_action, self._on_stop_service_action)
        self.framework.observe(self.on.run_action, self._on_run_action)
        self.framework.observe(self.on.health_check_action, self._on_health_check_action)
        self.framework.observe(self.on.start_configuration_action, self._on_start_configuration_action)


    def _on_start_configuration_action(self, event):
        """Configure Snort service"""
        try:
            result = subprocess.run(["hostname","-I"], check=True, capture_output=True, text=True)
            output = result.stdout.split(' ')
            output.pop(-1)

            index = 0
            for value in output:
                if "f" in value:
                    output.pop(index)
                else:
                    ipaddress = value.split('.')
                    output[index] = ipaddress[0] + "." + ipaddress[1] + "." + ipaddress[2] + "." + "0" + "/24"
                index += 1

            line = "%YAML 1.1\n" + "---\n\n" + "vars:\n" + "  address-groups:\n"  + "    HOME_NET: \"[" + ",".join(str(x) for x in output) + "]\""
            with open("/etc/suricata/suricata.yaml", "r+") as f:
                content = f.read()
                with open("/etc/suricata/suricata.yaml", "w+") as f:
                    f.write(line + '\n' + content)

            result = subprocess.run(["ls","/sys/class/net"], check=True, capture_output=True, text=True)
            output = result.stdout.split('\n')
            interface = ""

            for value in output:
                if (("ens" in value) or ("eth" in value) or ("eno" in value)) and (len(value) < 6):
                    interface = value

            change = False
            with fileinput.FileInput("/etc/suricata/suricata.yaml", inplace = True, backup ='.bak') as f:
                for line in f:
                    if("af-packet:\n" == line):
                        change = True
                        print(line, end ='')
                        continue
                    elif (change == True):
                        print("  - interface: " + interface, end ='\n')
                        change = False
                    else:
                        print(line, end ='')

            event.set_results({
                "output": f"Start-configuration: Suricata service configured correctly"
            })
        except Exception as e:
            event.fail(f"Start-configuration: Suricata service configuration failed with the following exception: {e}")


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


    def _on_health_check_action(self, event):
        """Check if Suricata service is running"""
        try:
           result = subprocess.run(["service","suricata","status"], check=True, capture_output=True, text=True)
           output = result.stdout.split(' ')
           if "not" in output:
                event.set_results({
                     "output": f"Status: Suricata is not running"
                })
           else:
                listOfProcObjects = []
                for proc in psutil.process_iter():
                    pinfo = proc.as_dict(attrs=['name', 'cpu_percent'])
                    pinfo['ram_usage'] = self.get_size(proc.memory_info().vms)
                    if pinfo['name'] == 'Suricata-Main' and pinfo['ram_usage'] != "0.00B":
                        listOfProcObjects.append(pinfo);
                    io = psutil.net_io_counters()
                    net_usage = {"bytes_sent": self.get_size(io.bytes_sent), "bytes_recv": self.get_size(io.bytes_recv)}
                event.set_results({
                     "output": f"Status: Suricata is running",
                     "service-usage": listOfProcObjects,
                     "network-usage": str(net_usage)
                })

        except Exception as e:
           event.fail(f"Command: Health-check failed with the following exception: {e}")


    def _on_add_rule_action(self, event):
        """Add rule to Suricata config"""
        line = event.params["rule"]
        try:
            with open("/etc/suricata/rules/local.rules", "r+") as f:
                content = f.read()
                with open("/etc/suricata/rules/local.rules", "w+") as f:
                    f.write(line + '\n' + content)

            event.set_results({
                "output": f"Add-rule: New rule inserted successfully"
            })
        except Exception as e:
            event.fail(f"Add-rule: Add-rule failed with the following exception: {e}")


    def _on_del_rule_action(self, event):
        """Delete last rule to Suricata config"""
        try:
            with open("/etc/suricata/rules/local.rules", "r+") as f:
                content = f.read().splitlines(True)
                with open("/etc/suricata/rules/local.rules", "w+") as f:
                    f.writelines(content[1:])

            event.set_results({
                "output": f"Del-rule: Last rule removed successfully"
            })
        except Exception as e:
            event.fail(f"Del-rule: Del-rule failed with the following exception: {e}")


    def _on_start_service_action(self, event):
        """Start Suricata service"""
        try:
            subprocess.run(["service","suricata","start"], check=True, capture_output=True, text=True)
            event.set_results({
                "output": f"Start: Suricata service started successfully"
            })
        except Exception as e:
            event.fail(f"Start: Suricata service starting failed with the following exception: {e}")


    def _on_stop_service_action(self, event):
        """Stop Suricata service"""
        try:
            subprocess.run(["service","suricata","stop"], check=True, capture_output=True, text=True)
            event.set_results({
                "output": f"Start: Suricata service stopped successfully"
            })
        except Exception as e:
            event.fail(f"Start: Suricata service stopping failed with the following exception: {e}")


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

#        kubernetesResources = {"pod": {"hostNetwork": True}}

        self.model.pod.set_spec({"version": 3, "containers": containers}) #, "kubernetesResources": kubernetesResources})

        self.unit.status = ActiveStatus()
        self.app.status = ActiveStatus()


    def get_size(self, bytes):
        """
        Returns size of bytes in a nice format
        """
        for unit in ['', 'K', 'M', 'G', 'T', 'P']:
            if bytes < 1024:
                return f"{bytes:.2f}{unit}B"
            bytes /= 1024



if __name__ == "__main__":
    main(SuricataCharm)
