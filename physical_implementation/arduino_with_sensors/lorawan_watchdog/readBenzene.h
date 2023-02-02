#ifndef readBenzene_h
#define readBenzene_h

#include <Arduino.h> 
#include <MQ135.h>

#define dataPinB A2 // pin connected to the Board

// MQ135:
MQ135 mq135_sensor(dataPinB);

// MQ135:
float readBenzene(float Temp, float Hum){
  // To get reliable data reads from the sensor its important to calibrate it correctly.
  // We can do this by placing it outdoor (ideal conditions: 20 degrees, 33% humidity), let it run for 12-24 hours to "burn it" and stabilize it.
  // Then, whilst remaining outdoor, we can read RZero value.
  //float rzero = gasSensor.getRZero();
  // OSS: best way to do this is by doing multiple reads to combat also the ADC noise.
  // After calibration is finished, we will pass RZero to our constructor like this:
  //MQ135 mq135_sensor(PIN_MQ135, rzero);
  Serial.println("MQ135 => Detecting Benzene..  ");

  //Change the values between parenthesis in the following section with the values passed as parametres.
  float correctionFactor = mq135_sensor.getCorrectionFactor(Temp, Hum);
  float rload = mq135_sensor.getResistance();
  float correctedRLoad = mq135_sensor.getCorrectedResistance(Temp, Hum);
  float rzero = mq135_sensor.getRZero();
  float correctedRZero = mq135_sensor.getCorrectedRZero(Temp, Hum);
  float resistance = mq135_sensor.getResistance();
  float ppm = mq135_sensor.getPPM();
  float correctedPPM = mq135_sensor.getCorrectedPPM(Temp, Hum);

  delay(2000);
  return correctedPPM;
}

#endif
