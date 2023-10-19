# Security Capabilities (SC) / Security as a Service (SecaaS)

This is the official PALANTIR repository where the Security Capabilities (SCs) functionality, configuration, descriptors, and interfaces are allocated.

## Structure definition

The repository contains different information related with SCs:

- [deployment-images](https://gitlab.com/palantir-project/sc-secaas/-/tree/master/deployment-images): it includes the deployment files to create the docker images that incorporates all the logic of the different SCs.
- [descriptor-packages](https://gitlab.com/palantir-project/sc-secaas/-/tree/master/descriptor-packages): it contains the files required for the on-boarding and instantiating of SCs in the Security Capabilities Orchestrator (SCO).
- [helm-charts](https://gitlab.com/palantir-project/sc-secaas/-/tree/master/helm-charts): it allocates the implementation of the helm-charts for each complex SC implemented. The files, implemented code and interesting information of such SCs is available in the respective folder.
- [juju-charms](https://gitlab.com/palantir-project/sc-secaas/-/tree/master/juju-charms): it allocates the implementation of the juju-charms for each SC implemented. The files, implemented code and interesting information of such SCs is available in the respective folder.
- [tools](https://gitlab.com/palantir-project/sc-secaas/-/tree/master/tools): it includes preparatory scripts for some of the SCs implemented. Here, we can find the SIEM SC installation files to be installed in the agents for both Linux and Windows agents.
- [usecase1](https://gitlab.com/palantir-project/sc-secaas/-/tree/master/UseCase1/Y1-Scenario): this folder incorporates the demo designed to demonstrate the functioning of the different SCs deployed for the Use Case 1. Besides, a folder appears inside of it for the year of creation.

## User Guide
Into the specific folder, the necessary commands for the proper use are explained, as well as possible interesting information needed to produce a successful functioning and integration of SCs into the PALANTIR platform.

