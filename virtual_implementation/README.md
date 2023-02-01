# Virtual implementation
 
The code is structured as follows:
* main.py → is the main file, the list of the devices previously added on ChirpStack are retrieved and the virtual watchdogs are assigned to the virtual gateways. An interface is shown to the user with buttons that start threads that simulate the behavior of the devices.
* thread_appserver.py, thread_edgenode.py, thread_watchdog.py → contain the definition of threads that simulate physical devices
* appserver.py, edgenode.py, watchdog.py → contain the functions that are called by the related threads necessary to simulate the devices.

## Installation Guide
1. Download the .ova file available at this link: https://drive.google.com/file/d/16Z0TCVcng6uvKk0f9RyPKdaf4MYYknwI/view?usp=sharing.
2. Open VirtualBox and click on 'file' > import appliance > and select the .ova file. Click next and finish.
3. Select the imported machine > settings > network and press ‘ok’.
4. Click on start button or double click on the imported machine. The username is “chirpstack” and the password is “admin”. 
5. Type in the CLI the command “hostname -I” to discover the ip address of the Server.
6. Open the browser and type *server_ipaddress*:9000. Login on Portainer (username is “admin” and password is “adminadminadmin”), click on ‘local’, then ‘container’ and make sure that containers are running.
7. Download *chirpstack_ws* and install the dependencies specified in *dependencies.txt*
8. Open *setup.py* in virtual_implementation/chirpstack_ws and replace the “broker_server” value with your server ip address.
9. Run *the main.py* file, a window appears. Click on start AppServer, then Start gateways and in the end Start watchdog. Check the system behavior with the Console Log of every component.

## Chirpstack AppServer
The ChirpStack AppServer installed with the Virtual Machine provides a web-interface (reachable through *server_ip_address*:8080) in which there are already the following virtual devices:
* 2 Gateways:
    * vGateway1
    * vGateway2
* 2 Watchdogs:
    * vWatchDog1	
    * vWatchDog2

However it is possible to add new custom devices.