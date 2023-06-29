#! /usr/bin/env python3

import logging
from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, MaintenanceStatus
import time
import subprocess
import psutil
logger = logging.getLogger(__name__)

class wgServices(CharmBase):

    def __init__(self, *args) -> None:
        self.server_name = "wg0"
        self.free_IP_list = list()
        for i in range(1,11):
            ip = "192.168.1."
            aux = 200 + i
            ip = ip + str(aux) +"/32"
            self.free_IP_list.append(ip)
        self.server_public_ip = ""

        """Initialize charm and configure states and events to observe."""
        super().__init__(*args)
        self.framework.observe(self.on.config_changed, self.configure_pod)
        self.framework.observe(self.on.init_config_action, self._on_init_config_action)
        self.framework.observe(self.on.get_server_data_action,self._on_get_server_data_action)
        self.framework.observe(self.on.add_client_action, self._on_add_client_action)
        self.framework.observe(self.on.disconnect_client_action, self._on_disconnect_client_action)
        self.framework.observe(self.on.disconnect_server_action, self._on_disconnect_server_action)
        self.framework.observe(self.on.health_check_action, self._on_health_check_action)


    def checkInterface(self, interface_list):
        result = subprocess.run(["ls","/sys/class/net"], check=True, capture_output=True, text=True)
        output = result.stdout.split('\n')
        interface = ""
        for interface in output: #Wired: en (enps1, eno1 or ens1) and eth (eth0) | Wifi: wl (wlan wlp)
            if (("en" in interface) or ("wl" in interface)  or ("eth" in interface)) and (len(interface) < 8):
            
                for current_interface in interface_list:
                    if current_interface in interface:
                        interface_path = "/sys/class/net/" + interface + "/operstate"
                        cat_process = subprocess.Popen(["cat", interface_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE,text=True)
                        output,err = cat_process.communicate()
                        interface_status = output.split(sep="\n")
                        if interface_status[0] == "up":
                            return interface                    
        return "-1"

    def generate_keys(self):
        file = open('/etc/wireguard/public_key.key.pub', 'w')

        processWg = subprocess.Popen(["wg", "genkey"], stdout=subprocess.PIPE)

        processTee = subprocess.Popen(["tee", "/etc/wireguard/private_key.key"], stdin=processWg.stdout, stdout=subprocess.PIPE) 

        processPubkey = subprocess.Popen(["wg","pubkey"], stdin=processTee.stdout, stdout=file)

        processChmod = subprocess.Popen(["chmod", "600", "/etc/wireguard/private_key.key", "/etc/wireguard/public_key.key.pub" ])

        file.close()
        time.sleep(1)

    def _on_init_config_action(self, event):
        self.generate_keys()
        interface_list = ["enp","eno","ens","eth","wlan","wlp"]
        iface_name = self.checkInterface(interface_list)
        server_listening_port = "41194"
        if(iface_name != None):
            try:
                file_server_priv_key = open("/etc/wireguard/private_key.key",'r')
                server_priv_key = file_server_priv_key.readline()
                file_server_priv_key.close()
                
                process_dig = subprocess.run(["dig", "+short", "myip.opendns.com", "@resolver1.opendns.com"], capture_output=True, text=True)
                self.server_public_ip = process_dig.stdout.splitlines()[0]

                conf_file = open("/etc/wireguard/"+ self.server_name + ".conf","w")
                conf_file.write(
                "[Interface]\n"
                + "Address = 192.168.1.200\n"
                + "PrivateKey = " + server_priv_key
                + "ListenPort = " + server_listening_port + "\n"
                + "PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A POSTROUTING -o " + iface_name + " -j MASQUERADE \n"
                + "PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D POSTROUTING -o " + iface_name + " -j MASQUERADE \n"
                + "SaveConfig = true\n")
                conf_file.close()
                time.sleep(1)

                subprocess.run(["wg-quick", "up", self.server_name],capture_output=True, text=True)
                time.sleep(1)

                wg_command = subprocess.run(["wg"], capture_output=True, text=True)
                wg_text = wg_command.stdout.splitlines()
                wg_output = ""
                for lines in wg_text:
                    wg_output = wg_output + lines + "\n"

                event.set_results({
                    "output": f"Server started successfully:\n{wg_output}"
                })

            except Exception as e:
                event.fail(f"Server initiation failed due an unespected exception named: {e}")
        else:
            event.fail(f"Server initiation failed due a problem with network interfaces: {e}")

    def _on_get_server_data_action(self, event):
        try:
       
            process_dig = subprocess.run(["dig", "+short", "myip.opendns.com", "@resolver1.opendns.com"], capture_output=True, text=True)
            self.server_public_ip = process_dig.stdout.splitlines()[0]

            wg_command = subprocess.run(["wg"], capture_output=True, text=True)
            wg_text = wg_command.stdout.splitlines()
            wg_output = ""
            for lines in wg_text:
                wg_output = wg_output + lines + "\n"
            event.set_results({
                    "output": f"Server with public IP {self.server_public_ip} started successfully:\n{wg_output}"
            })
        except Exception as e:
            event.fail(f"Server data failed due an unespected exception named: {e}")

    def _on_add_client_action(self, event):
        try:
            
            client_key_string = event.params["public-key"]

            server_config_process = subprocess.Popen(["wg", "show"], stdout=subprocess.PIPE)
            grep_process = subprocess.Popen(["grep", "-o","192.168.1.*"],  stdin=server_config_process.stdout, stdout=subprocess.PIPE)
            output, _ = grep_process.communicate()
            lines = output.decode()

            no_ip = True
            while no_ip:
                if len(self.free_IP_list) > 0:
                    client_ip = self.free_IP_list.pop(0)
                    if client_ip not in lines:
                        no_ip = False
                        subprocess.run(["wg", "set", self.server_name,"peer", client_key_string, "allowed-ips", client_ip, "persistent-keepalive", "25"])

                        subprocess.run(["wg-quick", "down", self.server_name],capture_output=True, text=True)
                        subprocess.run(["wg-quick", "up", self.server_name],capture_output=True, text=True)

                        event.set_results({
                                "output": f"This is your private IP: {client_ip}\nClient added\n"
                        })
                        return
                else:
                    break
            event.set_results({
                "output": f"No IPs available"
            })        

        except Exception as e:
            event.fail(f"Server failed due an unespected exception named: {e}")

    def _on_disconnect_client_action(self, event):
        
        try:
            client_key_string = event.params["public-key"]
            client_priv_ip = event.params["ip"]
            
            server_config_process = subprocess.run(["wg", "show"],  capture_output=True, text=True)
            lines = server_config_process.stdout.splitlines()

            index = 0
            check_client = False
            for line in lines:
                if client_key_string in line:
                    key_index = index
                    if client_priv_ip in lines[key_index+2]:
                        check_client = True
                        continue
                index += 1
            
            if check_client == True:
                subprocess.run(["wg", "set", self.server_name,"peer", client_key_string ,"remove"])
                subprocess.run(["wg-quick", "down", self.server_name],capture_output=True, text=True)
                subprocess.run(["wg-quick", "up", self.server_name],capture_output=True, text=True)
                event.set_results({
                    "output": f"Client removed\n"
                })
            else:
                event.set_results({
                    "output": f"Client data is not correct. Please, check the params.\n"
                })
        except Exception as e:
            event.fail(f"Server failed due an unespected exception named: {e}")

    def _on_disconnect_server_action(self, event):
        try:
            subprocess.run(["wg-quick", "down", self.server_name], capture_output=True, text=True)
            file_route = "/etc/wireguard/" + self.server_name + ".conf"
            open(file_route, 'w').close()

            event.set_results({
                "output" :  f"Server disconnected."
            })
        except Exception as e:
            event.fail(f"Server failed due to an unexpected exception while disconnecting.: {e}")


    def to_bytes(self, number, units):
        total_bytes = 0.00
        if units == "KiB":
            total_bytes = number * (2**10)
        elif units == "MiB":
            total_bytes = number * (2**20)
        elif units == "GiB":
            total_bytes = number * (2**30)
        elif units == "TiB":
            total_bytes = number * (2**40)
        return total_bytes
    
    def convert_bytes(self, byte_value):
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        base = 1024
    
        if byte_value < 0:
            raise ValueError("Byte value must be a non-negative number")
    
        unit_index = 0
        while byte_value >= base and unit_index < len(units) - 1:
            byte_value /= base
            unit_index += 1
    
        return byte_value, units[unit_index]
    
    def _on_health_check_action(self, event):
        """Stop Wireguard service"""
        try:

            wg_command = subprocess.run(["wg"], capture_output=True, text=True)
            wg_text = wg_command.stdout.splitlines()
            connected = len(wg_text)
            if connected > 0:
                list_of_proc_objects = []
                ps_info = {"name": "wg-quick", "cpu_percent": "0.0", "ram_usage": "0.00"}
                list_of_proc_objects.append(ps_info)

                server_config_process = subprocess.Popen(["wg", "show"], stdout=subprocess.PIPE)
                grep_process = subprocess.Popen(["grep", "transfer"],  stdin=server_config_process.stdout, stdout=subprocess.PIPE)
                output, _ = grep_process.communicate()
                string_lines = output.decode()
                list_lines = string_lines.split()
                size_list = len(list_lines)

                if size_list > 0:
                    total_lines = size_list // 7
                    accumulated_received = 0
                    accumulated_sent = 0
                    for i in range(0,total_lines,1):
                        index_number_received = 1 + (7*i)
                        index_unit_received = 2 + (7*i)
                        index_number_sent = 4 + (7*i)
                        index_unit_sent = 5 + (7*i)
                        number_received = self.to_bytes(float(list_lines[index_number_received]), list_lines[index_unit_received])
                        number_sent = self.to_bytes(float(list_lines[index_number_sent]), list_lines[index_unit_sent])
                        accumulated_received = accumulated_received + number_received
                        accumulated_sent = accumulated_sent + number_sent
                    total_received,unit_received = self.convert_bytes(accumulated_received)
                    total_sent,unit_sent = self.convert_bytes(accumulated_sent)
                    net_usage={"bytes_sent": str(round(total_sent,2)) + unit_sent , "bytes_recv": str(round(total_received,2)) + unit_received}

                    event.set_results({
                        "output": f"Status: Wireguard is running",
                        "service-usage": list_of_proc_objects,
                        "network-usage": str(net_usage)
                    })
                    return
                
                else:
                    net_usage={"bytes_sent": "0", "bytes_recv": "0"}
                    event.set_results({
                        "output": f"Status: Wireguard is running, but no currently active connections",
                        "service-usage": list_of_proc_objects,
                        "network-usage": str(net_usage)
                    })
                    return

            else:
                event.set_results({
                    "output": f"Wireguard: Wireguard service is not running"
                })
        except Exception as e:
            event.fail(f"Health-check: Health-check status failed with the following exception: {e}")


    def configure_pod(self, event):
        if not self.unit.is_leader():
            self.unit.status = ActiveStatus()
            return
        self.unit.status = MaintenanceStatus("Applying pod spec")
        containers = [
            {
                "name": self.framework.model.app.name,
                "image": "jeffreysilver/wireguard_server:kubernetes",
                "ports": [
                    {
                        "name": "wireguard",
                        "containerPort": 41194,
                        "protocol": "UDP",
                    }
                    ,
                    {   
                        "name": "iptnetflow",
                        "containerPort": 25,
                        "protocol": "UDP",
                    }
                ],
                "command": ["/bin/bash","-ce","tail -f /dev/null"],
                "kubernetes": { "securityContext": { "privileged": True}}
            }            
        ]

        kubernetesResources = {"pod": {"hostNetwork": True}}

        self.model.pod.set_spec({"version": 3, "containers": containers, "kubernetesResources": kubernetesResources})

        self.unit.status = ActiveStatus()
        self.app.status = ActiveStatus()

if __name__ == "__main__":
    main(wgServices)
