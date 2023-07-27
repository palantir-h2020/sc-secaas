#! /usr/bin/env python3
import json
import sqlite3
from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, MaintenanceStatus
import time
import subprocess
import psutil
import requests


class ntopng_server(CharmBase):
    def __init__(self, *args) -> None:
        self.ntopng_data_path = "/home/ntopng_data/"

        super().__init__(*args)

        self.framework.observe(self.on.config_changed, self.configure_pod)
        self.framework.observe(self.on.launch_ntopng_action,self._on_launch_ntopng_action)
        self.framework.observe(self.on.stop_ntopng_action,self._on_stop_ntopng_action)
        self.framework.observe(self.on.rrd_action,self._on_rrd_action)
        self.framework.observe(self.on.get_alerts_action,self._on_get_alerts_action)
        self.framework.observe(self.on.health_check_action, self._on_health_check_action)
        self.framework.observe(self.on.get_top_talkers_action,self._on_get_top_talkers_action)

    def _on_launch_ntopng_action(self, event):
        try:
            id_interface = str(event.params["id-interface"])
            
            headers =  {"Content-Type":"application/json"}
            data = '{"id_interface": "' + id_interface + '", "ntopng_data_path": "' + self.ntopng_data_path + '"}'
            result = requests.post('http://localhost:5001/start-ntopng', headers=headers, data=data, verify=False)

            event.set_results({
                "output": str(result.json())
            })

        except Exception as e:
            event.fail(f"Server initiation failed due an unespected exception named: {e}")


    def _on_stop_ntopng_action(self, event):
        try:
            result = requests.get('http://localhost:5001/stop-ntopng', verify=False)
            event.set_results({
                "output": str(result.json())
            })

        except Exception as e:
            event.fail(f"Server stop failed due an unespected exception named: {e}")


    def _on_rrd_action(self, event):
        try:

            id_interface = str(event.params["id-interface"])
            type_file = event.params["type-file"]
            path = self.ntopng_data_path + id_interface + "/rrd/" + type_file + ".rrd"

            if type_file == "alerted_flows" or type_file == "num_hosts" or type_file == "traffic_anomalies_v2" or type_file == "dropped_alerts":
                aux = subprocess.run(["rrdtool", "dump",  path], check=True, capture_output=True, text=True)
                aux_output = aux.stdout.split('\n')
                file_data = list()

                for i in range (0,22): #Take headers
                    file_data.append(aux_output[0 + i])

                for i in range(0, 1500): #Get the last element since <params> or 1500 lines
                    elem = aux_output.pop()
                    if "<rra>" in elem:
                        file_data.insert(22,elem)
                        break
                    file_data.insert(22,elem)
                output = ""
                for elem in file_data:
                    output = output + elem + "\n"

                event.set_results({
                    "output": f"{output}"
                })
            else:
                output = "Introduce one of this rrd name files:\n\t alerted_flows\n\t num_hosts\n\t traffic_anomalies_v2\n\t dropped_alerts\n"
                event.set_results({
                    "output": f"{output}"
                })

        except Exception as e:
            output = "Introduce one of this rrd name files:\n\t alerted_flows\n\t num_hosts\n\t traffic_anomalies_v2\n\t dropped_alerts\n"
            event.fail(f"rrd action failed due an unespected exception named: {e} \n {output}")


    def _on_get_alerts_action(self, event):
        try:

            id_interface = event.params["id-interface"]
            type_alert = event.params["type-alert"]
            dbfile = self.ntopng_data_path + str(id_interface) + '/alerts/alert_store_v11.db'
            con = sqlite3.connect(dbfile)
            cur = con.cursor()
            output = str()
            if type_alert == "active_monitoring_alerts" or type_alert == "flow_alerts" or type_alert == "host_alerts" or  type_alert == "mac_alerts" or type_alert == "snmp_alerts" or type_alert == "network_alerts" or type_alert == "interface_alerts" or type_alert == "system_alerts":
                if (type_alert == "flow_alerts"):
                    for row in cur.execute("SELECT * FROM " + type_alert): 
                        json_row = json.loads(row[9])
                        pretty_dict = json.dumps(json_row, indent=8)
                        output = output + pretty_dict
                else:
                    for row in cur.execute("SELECT * FROM " + type_alert): 
                        json_row = json.loads(row)
                        pretty_dict = json.dumps(json_row, indent=8)
                        output = output + pretty_dict
            else:
                output = 'Types to select:\t active_monitoring_alerts\n \t flow_alerts\n \t host_alerts\n \t mac_alerts\n \t snmp_alerts\n \t network_alerts\n \t interface_alerts\n \t system_alerts\n'
            
            con.close()

            event.set_results({
                "output": output
            })
        except Exception as e:
            event.fail(f"Get alerters failed due an unespected exception named: {e} \n Types to select:\t active_monitoring_alerts\n \t sqlite_sentence\n \t flow_alerts\n \t host_alerts\n \t mac_alerts\n \t snmp_alerts\n \t network_alerts\n \t interface_alerts\n \t system_alerts\n")

    def _on_get_top_talkers_action(self,event): 
        try:
            id_interface = str(event.params["id-interface"])

            dbfile = self.ntopng_data_path + id_interface + "/top_talkers/top_talkers.db"
            con = sqlite3.connect(dbfile)
            cur = con.cursor()
            output = str()
            aux_list = list()
            file_data = list()

            for row in cur.execute("SELECT * FROM MINUTE_STATS"):
                json_row = json.loads(row[1])
                pretty_dict = json.dumps(json_row, indent=8)
                aux_list.append(pretty_dict)
                time.sleep(0.2)
            
            while True: #Get the last 3 top talkers
                elem = aux_list.pop()
                if(len(aux_list) == 3):
                    file_data.insert(0,elem)
                    break
                file_data.insert(0,elem)

            for elem in file_data:
                output = output + elem

            con.close()
            
            event.set_results({
                "output": output
            })

        except Exception as e:
            event.fail(f"Get top talkers failed due an unespected exception named:\n {e}")

    def _on_health_check_action(self, event):
        """Health-check service"""
        try:
            listOfProcObjects = []
            for process in psutil.process_iter():
                if "ntopng-main" in process.name() and "zombie" not in process.status():
                    pinfo = process.as_dict(attrs=['name', 'cpu_percent'])
                    pinfo['ram_usage'] = self.get_size(process.memory_info().vms)
                    listOfProcObjects.append(pinfo)
                    io = psutil.net_io_counters()
                    net_usage = {"bytes_sent": self.get_size(io.bytes_sent), "bytes_recv": self.get_size(io.bytes_recv)}
                    event.set_results({
                        "output": f"Status: Ntopng is running",
                        "service-usage": listOfProcObjects,
                        "network-usage": str(net_usage)
                    })
                    return
            event.set_results({
                "output": f"Health-check: Ntopng is not running"
            })
        except Exception as e:
            event.fail(f"Health-check: Health-check status failed with the following exception: {e}")

    def get_size(self, bytes):
        """
        Returns size of bytes in a nice format
        """
        for unit in ['', 'K', 'M', 'G', 'T', 'P']:
            if bytes < 1024:
                return f"{bytes:.2f}{unit}B"
            bytes /= 1024
    
    
    #### 5. configure pod
    def configure_pod(self,event):
        if not self.unit.is_leader():
            self.unit.status = ActiveStatus()
            return
        self.unit.status = MaintenanceStatus("Applying pod spec")
        containers = [
            {
                "name": self.framework.model.app.name,
                "image": "jeffreysilver/ntopng_server:kubernetes",
                "ports": [

                    {   
                        "name": "ntopng",
                        "containerPort": 26,
                        "protocol": "UDP",
                    }
                ],
                "kubernetes": { "securityContext": { "privileged": True}}
            }            
        ]

        kubernetesResources = {"pod": {"hostNetwork": True}}

        self.model.pod.set_spec({"version": 3, "containers": containers, "kubernetesResources": kubernetesResources})

        self.unit.status = ActiveStatus()
        self.app.status = ActiveStatus()

if __name__ == "__main__":
    main(ntopng_server)
