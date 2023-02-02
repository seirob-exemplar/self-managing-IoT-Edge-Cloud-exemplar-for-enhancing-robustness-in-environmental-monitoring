#ifndef readTemperature_h
#define readTemperature_h

#include <Arduino.h>
#include <DHT.h> 

#define dataPinTU 1 // pin connected to the Arduino board
#define DHTType DHT22 // defining sensor model (type of it)

// DHT22:
DHT dht = DHT(dataPinTU, DHTType); //create the sensor object

// DHT22 (Temp):
float readTemp(){
  dht.begin();
  Serial.println("DHT22 => Detecting Temperature.. ");
  delay(2000); //refresh rate is 2 sec.
  float t = dht.readTemperature(); 
  return t;
}

#endif
