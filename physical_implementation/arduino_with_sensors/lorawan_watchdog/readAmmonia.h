#ifndef readAmmonia_h
#define readAmmonia_h

#include <Arduino.h> // 

#define dataPinA A1 // pin connected to the Arduino Board
#define RL 47  // Resistance of RL is 47 kohm
#define M -0.263 // Angular coefficent 
                 // Points: (x1;y1) e (x2;y2) --> (40;1) e (100;0.8) 
#define b 0.42 // Intercept value
               // Point: (x;y) --> (70;0.75)
#define Ro 30 // Ro value (calculated with the proper program)


// MQ137
float readAmmoniaca(){
  float analog_value; // We will need the average value of analog reads of the sensor, to convert later on in Voltage (tensione)
  float VRL; // Voltage in RL
  float Rs; // Resistor value at a given gas concentration.
  float ratio; // Represents Rs/Ro
  Serial.println("MQ137 => Detecting Ammonia concentration.. ");

  for(int i = 1 ; i <= 500 ; i++){ // read analog values 500 times.
    analog_value = analog_value + analogRead(dataPinA); // sum analog values
  }
  
  analog_value = analog_value/500.0; // average analogs value 
  VRL = analog_value*(5.0/1023.0); // convert analogic value to digital Voltage
  // if we would want to avoid the cycle: VRL = analogRead(MQ_sensor)*(5.0/1024.0); (measure voltage between 0V-5V)
  // Rs = ((Vc/VRL)-1)*RL o Rs = [(Vc*RL)/VRL]-RL is the formula corrisponding to the equivalent circuit of sensore MQ137
  Rs = ((5.0*RL)/VRL)-RL;
  ratio = Rs/Ro;  // Rs/Ro, no in a clean area scenario
  // Calculate ammonia concentration using inverse formula
  // formula m*log(x) + b
  // where: y = ratio
  //       x = ppm concentration
  //       m = angular coefficient
  //       b = intercept
  float ppm = pow(10, ((log10(ratio)-b)/(M)));

  delay(2000);
  return ppm;  
}

#endif
