#! /usr/bin/env python3

import logging

from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, MaintenanceStatus, BlockedStatus
import subprocess
import os
import psutil
import time
import requests

logger = logging.getLogger(__name__)


class IptnetflowCharm(CharmBase):
    """Class representing this Operator charm."""

    def __init__(self, *args):
        """Initialize charm and configure states and events to observe."""
        super().__init__(*args)

        self.framework.observe(self.on.config_changed, self.configure_pod)
        self.framework.observe(self.on.start_netflow_action, self._on_start_netflow_action)
        self.framework.observe(self.on.stop_netflow_action, self._on_stop_netflow_action)
        self.framework.observe(self.on.start_zeek_action, self._on_start_zeek_action)
        self.framework.observe(self.on.stop_zeek_action, self._on_stop_zeek_action)
        self.framework.observe(self.on.start_mirroring_action, self._on_start_mirroring_action)
        self.framework.observe(self.on.stop_mirroring_action, self._on_stop_mirroring_action)
        self.framework.observe(self.on.health_check_action, self._on_health_check_action)
        self.framework.observe(self.on.run_action, self._on_run_action)


    def _on_start_mirroring_action(self, event):
        """Start traffic mirroring process receiving the internal SC IP as input"""
        internal_ip = event.params["ip"]
        try:
            os.system("iptables -t mangle -A PREROUTING -j TEE --gateway " + internal_ip)
            os.system("iptables -t mangle -A POSTROUTING -j TEE --gateway " + internal_ip)
            event.set_results({
                "output": f"Traffic mirroring process started successfully"
            })
        except Exception as e:
            event.fail(f"Start traffic mirroring process failed with the following exception: {e}")


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
        """Health-check service"""
        try:
            listOfProcObjects = []
            for process in psutil.process_iter():
                if "softflowd" in process.name() and "zombie" not in process.status():
                    pinfo = process.as_dict(attrs=['name', 'cpu_percent'])
                    pinfo['ram_usage'] = self.get_size(process.memory_info().vms)
                    listOfProcObjects.append(pinfo);
                    io = psutil.net_io_counters()
                    net_usage = {"bytes_sent": self.get_size(io.bytes_sent), "bytes_recv": self.get_size(io.bytes_recv)}
                    event.set_results({
                        "output": f"Status: Iptables is running and Softflowd is running",
                        "service-usage": listOfProcObjects,
                        "network-usage": str(net_usage)
                    })
                    return
            event.set_results({
                "output": f"Health-check: Iptables is running but Softflowd is not running"
            })
        except Exception as e:
            event.fail(f"Health-check: Health-check status failed with the following exception: {e}")



    def _on_stop_mirroring_action(self, event):
        """Stop traffic mirroring process receiving the internal SC IP as input """
        internal_ip = event.params["ip"]
        try:
            os.system("iptables -t mangle -D PREROUTING -j TEE --gateway " + internal_ip)
            os.system("iptables -t mangle -D POSTROUTING -j TEE --gateway " + internal_ip)
            event.set_results({
                "output": f"Traffic mirroring process stopped successfully"
            })
        except Exception as e:
            event.fail(f"Stop traffic mirroring process failed with the following exception: {e}")


    def _on_start_zeek_action(self, event):
        """Start Zeek Collector"""
        try:
            result = requests.get('http://localhost:5000/start-zeek', verify=False)
            event.set_results({
                "output": str(result.json())
            })
        except Exception as e:
            event.fail(f"NetFlow collector stopping failed with the following exception: {e}")


    def _on_stop_zeek_action(self, event):
        """Stop Zeek Collectors"""
        try:
            result = requests.get('http://localhost:5000/stop-zeek', verify=False)
            event.set_results({
                "output": str(result.json())
            })
        except Exception as e:
            event.fail(f"NetFlow collector stopping failed with the following exception: {e}")


    def _on_stop_netflow_action(self, event):
        """Stop NetFlow Collectors"""
        try:
            result = requests.get('http://localhost:5000/stop-netflow', verify=False)
            event.set_results({
                "output": str(result.json())
            })
        except Exception as e:
            event.fail(f"NetFlow collector stopping failed with the following exception: {e}")


    def _on_start_netflow_action(self, event):
        """Start NetFlow Collector receiving the service where logs are sent as input"""
        ip = event.params["ip"]
        port = event.params["port"]
        iface = event.params["iface"]
        headers =  {"Content-Type":"application/json"}
        try:
            data = '{"ip": "' + ip + '", "port": ' + str(port) + ', "iface": "' + iface + '"}'
            result = requests.post('http://localhost:5000/start-netflow', headers=headers, data=data, verify=False)

            event.set_results({
                "output": str(result.json())
            })
        except Exception as e:
            event.fail(f"NetFlow collector failed with the following exception: {e}")

    def configure_pod(self, event):
        if not self.unit.is_leader():
            self.unit.status = ActiveStatus()
            return
        self.unit.status = MaintenanceStatus("Applying pod spec")
        containers = [
            {
                "name": self.framework.model.app.name,
                "image": "lopeez97/iptnetflow:1.0.6",
                "ports": [
                    {
                        "name": "iptnetflow",
                        "containerPort": 22,
                        "protocol": "TCP",
                    }
                ],
#                "command": ["/bin/bash","-ce","python3 app.py",],
                "kubernetes": { "securityContext": { "privileged": True}}
            }
        ]

        kubernetesResources = {"pod": {"hostNetwork": True}}

        self.model.pod.set_spec({"version": 3, "containers": containers, "kubernetesResources": kubernetesResources})

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
    main(IptnetflowCharm)
