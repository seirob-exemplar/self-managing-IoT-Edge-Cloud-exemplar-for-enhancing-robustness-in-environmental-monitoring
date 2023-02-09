# Virtual implementation
 
The code is structured as follows:
* main.py → is the main file for initializing anything: the list of the devices previously added on the ChirpStack Application Server are retrieved and the virtual watchdogs are assigned to the virtual gateways. An interface is shown to the user with buttons that start threads that simulate the behavior of the devices.
* thread_appserver.py, thread_edgenode.py, thread_watchdog.py → contain the definition of threads that simulate physical devices
* appserver.py, edgenode.py, watchdog.py → contain the functions that are called by the related threads necessary to simulate the devices.

## Installation Guide
1. Download the .ova file (it takes less than 30 minutes) available at this link: https://drive.google.com/file/d/16Z0TCVcng6uvKk0f9RyPKdaf4MYYknwI/view?usp=sharing.
2. Open VirtualBox (version 7.0 or higher) and click on 'file' > import appliance > and select the .ova file. Click next and finish.
3. Select the imported machine "Ubuntu Server" > settings > network and press ‘ok’.
4. Click on start button or double click on the imported machine. The username is “chirpstack” and the password is “admin”. 
5. Type in the CLI the command “hostname -I” to discover the ip address (*server_ipaddress*) of the Server. It should be the first IP address.
6. Open the browser on your (physical) computer and type *server_ipaddress*:9000. Login on Portainer.io (username is “admin” and password is “adminadminadmin”), click on ‘local’, then ‘container’ and make sure that all containers are running.
7. Download and unzip the code from this github, and go to the directory *virtual_implementation/chirpstack_ws* and install via the Python PIP tool the dependencies specified in *requirements.txt* (run each line separately in a console command of your computer). Note that we assume a recent version of Python is already installed on your computer.
8. Using your favourite Python IDE, open *setup.py* from virtual_implementation/chirpstack_ws and replace the “broker_server” variable value with your server *server_ipaddress*.
9. Run *the main.py* file; a dialog window should appear. Click in sequence on start AppServer, then Start gateways, and finally Start watchdog. Observe the system behavior with the Console Log of every component and the ChirpStack AppServer installed on the VM (reachable through *server_ip_address*:8080). 
 
The default IoT installation contains the following virtual devices:
* 2 Gateways:
    * vGateway1
    * vGateway2
* 2 Watchdogs:
    * vWatchDog1	
    * vWatchDog2
However it is possible to add new custom devices.


## Robustness scenarios
* Scenario S1 (Watchdog’s battery rationing): every time the AppServer receives a message from a watchdog, it checks its battery level and, based on this value, it sends a reconfiguration message to increase the parameters time-to-send and time-to-receive, and therefore increase the watchdog lifetime. Whenever a (downlink) configuration message is sent to a watcher, the AppServer console shows the message: *APPSERVER ENQUEQUE WATCHDOG watchdogname CONFIGURATION*. Subsequently, the watchdog console shows the following message: *CONFIGURED WATCHDOG: watchdogname - timetosend: value ms timetoreceive: value ms*. It means that the watchdog received the reconfiguration message and changed the parameters.

* Scenario S2 (High availability of watchdogs): every time the gateway receives a message from a watchdog, it forwards it to the AppServer and updates the knowledge variables associated to that watchdog (e.g., "last seen", last time the watchdog sent data). When "last seen" is greater than a threshold it means that the watchdog is not active and an error message is printed on the gateway console: *WATCHDOG watchdogname IS SILENT. LAST POSITION: {'latitude': lat, 'longitude': long}*. Subsequently, the gateway sends a message to the AppServer on the /silent/watchdog topic to notify that the watchdog is no longer active. AppServer prints on its console a message: *WATCHDOG watchdogname IS SILENT. LAST POSITION:{'latitude': lat, 'longitude': long}*

* Scenario S3 (High availability of edge nodes): the AppServer periodically checks if the gateways are alive by sending a message on the /command/ping topic. The gateways reply to the message by posting on the event/echo topic. If after 3 pings the AppServer does not receive an echo from a gateway, it prints an error message on its console: *EDGENODE gatewayname IS NOT WORKING. LAST POSITION: {'latitude': lat, 'longitude': long}*. Through the console of the AppServer and of the gateway it is possible to trace the system execution and observe its correct operation.



