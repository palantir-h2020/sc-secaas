#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.
"""OSM Config Library.

This library provides a simple way of getting information injected
by OSM in the osm-config configuration option.

# Schema

This is the JSON schema that is supported by the library
```json
{
    "v0": {
        "k8s" : {
            "services": {
                <service_name>: {
                    "ip": [<ip>],
                    "ports": {
                        <port_name>: {
                            "port": <port_number>,
                            "protocol": "TCP",
                        }
                    }
                }
            }
        }
    }
}
```

# Getting started

Execute the following command inside your Charmed Operator folder to fetch the library.

```shell
charmcraft fetch-lib charms.osm_libs.v0.osm_config
```

Import the library, and initialize it you charm constructor.

```python
# ...
from charms.osm_libs.v0.osm_config import OsmConfig

class SomeCharm(CharmBase):
    def __init__(self, *args):
        # ...
        self.osm_config = OsmConfig(self)
        # ...
```

# K8s services

The `OsmConfig` class allows you to easily get information about the K8s services
injected by OSM.

This is an example on how to get information the IP and port of a particular K8s service.

```python

class SomeCharm(CharmBase):
    def _on_some_action(self, event):
        openldap_service = self.osm_config.k8s.get_service("openldap")
        openldap_ip = openldap_service.ip
        openldap_port = openldap_service.get_port("openldap")
```
"""

import json
from typing import Any, Dict

from ops.charm import CharmBase

# The unique Charmhub library identifier, never change it/search
LIBID = "f5969a6bed59469dbe45f8016133c685"

# Increment this major API version when introducing breaking changes
LIBAPI = 0

# Increment this PATCH version before using `charmcraft publish-lib` or reset
# to 0 if you are raising the major API version
LIBPATCH = 1


class K8sService:
    """Represents a K8s Service."""

    def __init__(self, info):
        self.info = info

    @property
    def ip(self) -> str:
        """Get the first IP of the service."""
        return self.info["ip"][0]

    def get_port(self, port_name: str):
        """Get port by name.

        Args:
            port_name: Name of the port.
        """
        return self.info["ports"][port_name]["port"]


class K8sConfig:
    """Represents the K8s configuration in OsmConfig."""

    def __init__(self, k8s_config: Dict[str, Any]) -> None:
        self.config = k8s_config

    def get_service(self, service_name: str) -> K8sService:
        """Get K8s service by name.

        This function will only return one K8s service, the first that contains
        the `service_name` provided as argument.

        Args:
            service_name: Name of the K8s service.

        Returns:
            K8sService: the Kubernetes Service.
        """
        services = [
            service for s_name, service in self.get_services().items() if service_name in s_name
        ]
        return services[0] if len(services) > 0 else None

    def get_services(self) -> Dict[str, K8sService]:
        """Get all K8s services.

        Returns:
            Dict[str, K8sService]: Dictionary with service names as keys,
                and K8sService objects as values.
        """
        return {
            s_name: K8sService(s_values)
            for s_name, s_values in self.config.get("services", {}).items()
        }


class OsmConfig:
    """Represents the configuration injected by OSM."""

    option_name = "osm-config"
    version = f"v{LIBAPI}"

    def __init__(self, charm: CharmBase) -> None:
        # Check if option_name exists in the config options.
        if self.option_name not in charm.config:
            raise Exception(f"config option {OsmConfig.option_name} not provided.")
        self.config = json.loads(charm.config[OsmConfig.option_name])
        if OsmConfig.version not in self.config:
            raise Exception(f"version {OsmConfig.version} not present in osm-config.")
        self.k8s = K8sConfig(self.config[OsmConfig.version].get("k8s", {}))
