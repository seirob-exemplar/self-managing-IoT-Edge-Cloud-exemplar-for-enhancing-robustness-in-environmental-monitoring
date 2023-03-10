# SEIROB: SElf-managing-Iot-edge-cloud-exemplar-for-ROBust-environmental-monitoring

The aim of the project is to develop a self-adaptive IoT-Edge-Cloud exemplar for enhancing robustness in environmental monitoring.  The exemplar was realized using the Python programming language and the open-source ChirpStack LoRaWAN network server stack.  In our initial prototype, we assumed the environment to monitor has a map on which geolocated multi-sensor devices (sensor nodes) and gateways (edge nodes) can be deployed and connected using a single-hop routing model. So we assume the network coverage area is coverable by the radio range of single sensor nodes connected to gateways. 

An IoT-Edge-Cloud installation according to our exemplar’s network topology may consist of: sensor nodes, which are Arduino MKR-based hardware prototypes (developed in-house); edge nodes, which are Raspberry Pi-based LoRa gateways equipped with the ChirpStack Gateway OS; and server (or cloud) nodes hosting the Chirpstack network/application server. In the provided installation, the system is made up of: air quality watchdogs (the embedded software running on sensor nodes) that periodically read the air pollutant sensors' data and send it to the gateways as LoRa messages; gateways that forward sensor data to an application server (running on a cloud server node) via the Message Queue Telemetry Transport (MQTT) over TCP; a server (an Ubuntu Server installed on a virtual machine) hosting the LoRaWAN Network Server/Application server. In addition to the environmental data collection and direct transmission to a cloud server node for late processing, a semi-decentralized control software which uses additional controller components on edge nodes (gateways) is adopted for making decisions close to the sensor nodes. Specifically, runtime diagnostic services (MAPE-K loops) continuously run over edge/cloud nodes of the IoT system to discover device issues (e.g., low device’s battery level, silent nodes, etc.) and to automatically manage them thus reducing manual reconfiguration and hand-tuning. Appropriate Chirpstack event types (up, ack, join, echo, and status error events) and command types (down and ping) are represented by MQTT topics and used to trigger the feedback control functions/loops.

The exemplar project’s comprises simulated air quality watchers (running on sensor nodes), simulated LoRa gateways, and edge-cloud software controllers for offline experimentation; it also provides instructions for creating a physical setup made of Arduino-based watchdogs, edge controllers over real Raspberry Pi-based LoRa gateways, and a central network/application server for experimentation in the field. 
So, two artifacts types are available:
* [virtual_implementation](virtual_implementation), where all the devices (watchdog and gateway) are simulated through components written in Python.
* [physical_implementation](physical_implementation), that contains all the guides to create and configure all the physical devices and related software.

## Functioning in a nutshell
The system works as follows:
* The AppServer publishes a message on the */ping* topic and then waits for the response of the gateway on the */echo* topic. If the gateway doesn’t respond, the AppServer shows an error message with the last known position of the gateway.
* Gateways receive LoRa messages from Watchdogs and forward them to the AppServer. If a Watchdog doesn’t send data for a certain period of time it’s considered offline and an error message is displayed with the last known GPS-position of the watchdog.
* The behavior of the watchdog depends on two parameters, time-to-send and time-to-receive: every time-to-send seconds the watchdog sends data to the gateway and every time-to-receive seconds it checks for a downlink message containing re-configuration commands to execute as dicated by the decision making running over edge/cloud nodes. 
* Whenever the AppServer receives data from watchdog, it checks the battery level and if it’s below a certain threshold it sends a downlink message with a different time-to-send and time-to-receive in order to ration it.

## Contacts
[Patrizia Scandurra](mailto:patrizia.scandurra@unibg.it)
[Giuseppe Ruscica](mailto:giuseppe.ruscica@unibg.it)
[Filippo Barbieri](mailto:.barbieri4@studenti.unibg.it)
[Stefano Cattaneo](mailto:s.cattaneo24@studenti.unibg.it)
[Lorenzo Mazzoleni](mailto:mazzoleni17@studenti.unibg.it)
