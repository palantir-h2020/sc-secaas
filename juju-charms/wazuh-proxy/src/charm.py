#!/usr/bin/env python3

"""Wazuh charm."""

import json
import logging

from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, BlockedStatus

from wazuh import Wazuh


class Service:
    """Service Class."""

    def __init__(self, service_info: dict) -> None:
        self._service_info = service_info

    @property
    def ip(self):
        """Get service ip."""
        return self._service_info["ip"][0]

    def get_port(self, port_name):
        """Get port using port name."""
        return self._service_info["ports"][port_name]["port"]


class OsmConfig:
    """OsmConfig Class."""

    def __init__(self, charm: CharmBase) -> None:
        self._charm = charm
        self.log = logging.getLogger("osm.config")

    def get_service(self, service_name: str) -> Service:
        """Getting service object using service name."""
        osm_config = json.loads(self._charm.config["osm-config"])
        services = [
            s_values
            for s_name, s_values in osm_config["v0"]["k8s"]["services"].items()
            if service_name == s_name
        ]

        return Service(services[0])


class WazuhOperatorCharm(CharmBase):
    """Wazuh Charm."""

    def __init__(self, *args):
        """Constructor for Wazuh Charm."""
        super().__init__(*args)
        self.osm_config = OsmConfig(self)
        self.log = logging.getLogger("wazuh.operator")
        self.framework.observe(self.on.config_changed, self._on_config_changed)
        self.framework.observe(self.on.list_agents_action, self._on_list_agents_action)


    def _on_config_changed(self, _):
        """Handler for config-changed event."""
        osm_config = self.config.get("osm-config")
        if not osm_config:
            self.unit.status = BlockedStatus("osm-config missing")
            return
        self.log.info(f"osm-config={osm_config}")
        self.unit.status = ActiveStatus()

    def _get_wazuh_manager_instance(self) -> Wazuh:
        self.log.info("Creating Wazuh manager instance...")
        wazuh_service = self.osm_config.get_service("wazuh")
        wazuh_uri = f'https://{wazuh_service.ip}:{wazuh_service.get_port("api")}'
        self.log.info(f"Wazuh instance received with IP: {wazuh_uri}")

        return Wazuh(wazuh_uri)

    def _on_list_agents_action(self, event):
        """List agents connected to Wazuh workers."""
        try:
            self.log.info("Running list_agents action...")
            wazuh = self._get_wazuh_manager_instance()

            self.log.info("Wazuh instance received...")
            result = wazuh.list_agents()

            self.log.info(f"Result received: {result}")
            event.set_results({"output": str(result)})
        except Exception as e:
            event.fail(f"Failed to list wazuh agents: {e}")


if __name__ == "__main__":
    main(WazuhOperatorCharm)
