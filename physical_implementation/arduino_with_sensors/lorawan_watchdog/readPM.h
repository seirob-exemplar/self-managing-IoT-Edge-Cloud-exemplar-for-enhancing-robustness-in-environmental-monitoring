#ifndef readPM_h
#define readPM_h

#include <Arduino.h> 

int dataPinPM = 0;
unsigned long duration;
unsigned long starttime;
unsigned long sampletime_ms = 30000; // sampletime is 30s ;
unsigned long lowpulseoccupancy = 0; // represents Low Pulse Occupancy (LPO) got during the 30s sampling; // LPO: The sensor, regardless of particle intensity or size, counts the amount of time a particle is seen. // This amount of time, called Low Pulse Occupancy, can be seen as the "Opacity Percentage" of the air circulating through the sensor.
float ratio = 0;
float concentration = 0;

// Grove Dust Sensor PM10 =>
float readPM(){
  pinMode(dataPinPM,INPUT);
  Serial.println("Groove Dust Sensor => Detecting PM10 concentration..");
  starttime = millis(); //millis() get current time. We associate this value to starttime() to check the delta time elapsed in the while structure.
  while((millis()-starttime) < sampletime_ms){
  duration = pulseIn(dataPinPM, LOW); // pulseIn() read an impulse (both HIGH or LOW) on a pin ---- if value = HIGH then pulseIn() wait for the pin to change state to HIGH, starts counting, then it waits that the pin state changes to LOW and so, it stops counting. return impulse lenght in ms (0 if no impulse start in a determined interval).
  lowpulseoccupancy = lowpulseoccupancy+duration;
  }
  ratio = lowpulseoccupancy/(sampletime_ms*10.0);  // Percentage 0-100 (Integer value)
  concentration = 1.1*pow(ratio,3)-3.8*pow(ratio,2)+520*ratio+0.62; // According to the graph on the instructions.
  lowpulseoccupancy = 0;
  starttime = millis();
  return concentration;
}

#endif
