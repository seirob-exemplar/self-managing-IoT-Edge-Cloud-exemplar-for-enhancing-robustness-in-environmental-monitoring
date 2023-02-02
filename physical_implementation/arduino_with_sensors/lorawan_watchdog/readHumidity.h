#ifndef readHumidity_h
#define readHumidity_h

#include <Arduino.h> 
#include <DHT.h> 

#define dataPinTU 1 // pin connected to the Arduino board
#define DHTType DHT22 // defining sensor model (type of it)

// DHT22
//Why don't we put here the same line as in ReadTemperature.h?

// DHT22 (Hum.):

float readHum(){
  dht.begin();
  Serial.println("DHT22 => Detecting Humidity.. ");
  delay(2000); //refresh rate is 2 sec.
  float h = dht.readHumidity(); 
  return h;
}

#endif
