# SEIROB: SElf-managing-Iot-edge-cloud-exemplar-for-ROBust-environmental-monitoring

The aim of the project is to make an IoT system able to self-adapt to different usage scenarios thus reducing manual reconfiguration.
The system is made up of watchdogs that retrieve the data and send them to the gateways as LoRa messages. The gateways forward them to the Server. 
The server used is Ubuntu Server installed on a virtual machine. On the Server is installed ChirpStack, an open-source LoRaWAN Network Server which can be used to setup LoRaWAN networks.

Two versions are available:
* virtual_implementation, where all the devices (watchdog and gateway) are simulated through components written in Python.
* physical_implementation, that contains all the guides to create and configured all the physical devices.

## Functioning
The system works as follows:
* AppServer publishes a message on the */ping* topic and then waits for the response of the gateway on the */echo* topic. If the gateway doesn’t respond, the AppServer shows an error message with the last known position of the gateway.
* Gateways receive LoRa messages from Watchdogs and forward them to Server. If Watchdog doesn’t send data for a certain period of time it’s considered offline and an error message is displayed with the last known position of the watchdog.
The behavior of the watchdog depends on two parameters, time-to-send and time-to-receive: every time-to-send seconds the watchdog sends data to the gateway and every time-to-receive seconds it checks for a downlink message. 
* Whenever the AppServer receives data from watchdog, it checks the battery level and if it’s below a certain threshold it sends a downlink message with a different time-to-send and time-to-receive.

