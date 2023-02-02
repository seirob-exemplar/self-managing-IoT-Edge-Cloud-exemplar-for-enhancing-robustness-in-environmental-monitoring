#ifndef readOzone_h
#define readOzone_h

#include <Arduino.h> 
#include <MQ131.h>
#include "sensorsStates.h"

#define dataPinO A0

// MQ131:
float readOzono(bool calibrate){
  // MQ131: Start the sensor(we need 4 values).  Control (power of) heater (resistance) on pin 2  Analog reading of the sensor on pin A0 (output)
  // LOW_CONCENTRATION Model // The "sensitive material" of the MQ131 sensor is WO3 (Tungsten(VI) Oxide, i.e. Tungsten Trioxide or Tungstic Anhydride), which has a lower conductivity in clean air // When ozone is present, the conductivity of the material decreases as the concentration of the gas increases. The operation is therefore based on the conversion // of the change in conductivity in gas concentration via an output signal. (The sensor model LOW_CONCENTRATION is used for this)
  // Resistance RL of 1MOhms (1000000 Ohms)
  
  MQ131.begin(2, dataPinO, LOW_CONCENTRATION, 1000000); 
  
  if (calibrate){
  Serial.println("MQ131 => Calibration MQ131 in progress...");
  MQ131.calibrate();
  Serial.println("MQ131 => Calibration done!");
  }

  Serial.println("MQ131 => Detecting Ozone concentration.. ");
  // The calibration "fixes" 2 successive parameters: the value of R0 (base resistance) and the time required to warm up the sensor and obtain consistent and reliable readings
  
  //Serial.println("Sampling MQ131... ");
  MQ131.sample();

  // The sensor is sensitive to environmental variations (temperature and humidity). If you want to have correct values, you need to set the temperature and humidity before calling the getO3() function
  // with the setEnv() function. The temperature is in °C and the humidity in %. The values ​​should come from another sensor such as the DHT22.

  
  if (sensorsActiveFlags[1] == true and sensorsActiveFlags[2] == true){
  MQ131.setEnv(sensorsValues[1].toInt(),sensorsValues[2].toInt());
  Serial.println("MQ131 => Setting environmental values");
  }
  
  return (MQ131.getO3(PPM)/1000000);
}

#endif
