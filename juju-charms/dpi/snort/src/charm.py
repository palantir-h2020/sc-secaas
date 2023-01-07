#! /usr/bin/env python3

import logging

from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, MaintenanceStatus, BlockedStatus
import subprocess
import os
import psutil
import json

logger = logging.getLogger(__name__)


class SnortCharm(CharmBase):
    """Class representing this Operator charm."""

    def __init__(self, *args):
        """Initialize charm and configure states and events to observe."""
        super().__init__(*args)

        self.framework.observe(self.on.config_changed, self.configure_pod)
        self.framework.observe(self.on.start_configuration_action, self._on_start_configuration_action)
        self.framework.observe(self.on.add_rule_action, self._on_add_rule_action)
        self.framework.observe(self.on.del_rule_action, self._on_del_rule_action)
        self.framework.observe(self.on.start_service_action, self._on_start_service_action)
        self.framework.observe(self.on.stop_service_action, self._on_stop_service_action)
        self.framework.observe(self.on.health_check_action, self._on_health_check_action)
        self.framework.observe(self.on.run_action, self._on_run_action)


    def _on_start_service_action(self, event):
        """Start Snort service"""
        try:
            for process in psutil.process_iter():
                if "snort" in process.name() and "zombie" not in process.status():
                    event.set_results({
                        "output": f"Start: Snort service is already started"
                    })
                    return

            result = subprocess.run(["ls","/sys/class/net"], check=True, capture_output=True, text=True)
            output = result.stdout.split('\n')

            interface = "null"
            for value in output:
                if (("ens" in value) or ("eth" in value) or ("eno" in value)) and (len(value) < 6):
                    interface = value

            subprocess.Popen(['snort', '-D', '-i', interface, '-c', '/etc/snort/etc/snort.conf', '-l', '/var/log/snort'])
            os.system("service filebeat start")
            event.set_results({
                "output": f"Start: Snort service started successfully"
            })
        except Exception as e:
            event.fail(f"Stop: Snort service stopped failed with the following exception: {e}")


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

            line = "ipvar HOME_NET [" + ",".join(str(x) for x in output) + "]"
            with open("/etc/snort/etc/snort.conf", "r+") as f:
                content = f.read()
                with open("/etc/snort/etc/snort.conf", "w+") as f:
                    f.write(line + '\n' + content)

            event.set_results({
                "output": f"Start-configuration: Snort service configured correctly"
            })
        except Exception as e:
            event.fail(f"Start-configuration: Snort service configuration failed with the following exception: {e}")


    def _on_stop_service_action(self, event):
        """Stop Snort service"""
        try:
            for process in psutil.process_iter():
                if "snort" in process.name() and "zombie" not in process.status():
                    process.kill()
                    os.system("service filebeat stop")
                    event.set_results({
                        "output": f"Stop: Snort service stopped successfully"
                    })
                    return

            event.set_results({
                "output": f"Stop: Snort service is not running"
            })
        except Exception as e:
            event.fail(f"Stop: Snort service stopped failed with the following exception: {e}")


    def _on_health_check_action(self, event):
        """Stop Snort service"""
        try:
            listOfProcObjects = []
            for process in psutil.process_iter():
                if "snort" in process.name() and "zombie" not in process.status():
                    pinfo = process.as_dict(attrs=['name', 'cpu_percent'])
                    pinfo['ram_usage'] = self.get_size(process.memory_info().vms)
#                        if pinfo['name'] == 'snort' and pinfo['ram_usage'] != "0.00B":
                    listOfProcObjects.append(pinfo);
                    io = psutil.net_io_counters()
                    net_usage = {"bytes_sent": self.get_size(io.bytes_sent), "bytes_recv": self.get_size(io.bytes_recv)}
                    event.set_results({
                        "output": f"Status: Snort is running",
                        "service-usage": listOfProcObjects,
                        "network-usage": str(net_usage)
                    })
                    return
            event.set_results({
                "output": f"Stop: Snort service is not running"
            })
        except Exception as e:
            event.fail(f"Health-check: Health-check status failed with the following exception: {e}")


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
        line = event.params["rule"]
        try:
            with open("/etc/snort/rules/local.rules", "r+") as f:
                content = f.read()
                with open("/etc/snort/rules/local.rules", "w+") as f:
                    f.write(line + '\n' + content)

            event.set_results({
                "output": f"Add-rule: New rule inserted successfully"
            })
        except Exception as e:
            event.fail(f"Add-rule: Add-rule failed with the following exception: {e}")


    def _on_del_rule_action(self, event):
        """Delete last rule inserted to Snort config"""
        try:
            with open("/etc/snort/rules/local.rules", "r+") as f:
                content = f.read().splitlines(True)
                with open("/etc/snort/rules/local.rules", "w+") as f:
                    f.writelines(content[1:])

            event.set_results({
                "output": f"Del-rule: Last rule removed successfully"
            })
        except Exception as e:
            event.fail(f"Del-rule: Del-rule failed with the following exception: {e}")


    def configure_pod(self, event):
        if not self.unit.is_leader():
            self.unit.status = ActiveStatus()
            return
        self.unit.status = MaintenanceStatus("Applying pod spec")
        containers = [
            {
                "name": self.framework.model.app.name,
                "image": "lopeez97/snort2:latest",
                "ports": [
                    {
                        "name": "snort2",
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
    main(SnortCharm)
