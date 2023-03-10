# SEIROB:-SElf-managing-Iot-edge-cloud-exemplar-for-ROBust-environmental-monitoring

The watchdog node is represented by an Arduino MKR 1300 board. Two versions of the physical device are available:
* with sensors, the Arduino has sensors to monitor the air quality. 
* without sensors, the Arduino has only LoRa Antenna mounted to comunicate with Gateway and simulate randomly air quality data.

Both devices have no battery and simulate discharging with a randomly generated parameter at each cycle

## Modules 
The Arduino with sensors has the following modules mounted onto it:

* Bread Board
* LoRa Antenna
* Groove Dust Sensor → PM10
* DHT22 → Temperature & Humidity
* MQ131 → Ozone
* MQ135 → Benzene
* MQ137 → Ammonia
* MQ138 → Aldehydes
* NEO BLOX U6M → GPS

## Code Structure

The code consists of several files, in particular:

* lorawan_watchdog.ino → It represents the starting point of the program. Global variables are declared, libraries and other modules are imported, connection with the edge-nodes is realized (inside setup()) and loop() function, which contain the whole logic regarding the functioning of the watchdog, is defined.
* arduino_secrets.h and sensorsStates.h → These two files contain globally used data structures. in particular arduino_secrets contains the appEui and appKey ,which are sensitive keys used in the connection to chirpstack, while sensorsStates contains a set of arrays that serves to lighten the code.
* functions.h → This file contains the declaration and definition of all necessary functions used by the watchdog.
* everything else → For each pollutant to detect we have created a separate function file to properly manage their executions and define other useful variables needed for the calculation of the desired value.

## Sensors Position

Since we have chosen a positional solution, here is the order chosen for the sensors in the various arrays of sensorsStates.h:
  0 - PM10
  1 - Temperature 
  2 - Humidity
  3 - Ozone
  4 - Benzene
  5 - Ammonia
  6 - Aldehydes 
  7 - GPS

