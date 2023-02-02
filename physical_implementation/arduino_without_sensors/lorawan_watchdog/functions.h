#ifndef functions_h
#define functions_h

#include "sensorsStates.h" 

/* EXTERN VARIABLES -- IMPORTED FROM LORAWAN_WATCHDOG.INO*/
extern LoRaModem modem; 
extern int timetosend; 
extern int timetoreceive;

/* Variables + Initiliazing Values */
float battery = 100; // Simulate the battery draining via this variable


/* Functions Declarations */ 

// Read all the active sensor data and get an output string.
String read_data_from_sensor();

// Transfer data acquired to gateway
int send_data_to_gateway(String msg);

// Connect to gateway
int connect_to_gateway(String ae, String ak);

// Getting conf_data string
String exchange_data_with_gateway();

// Analyse conf_data and assign each value got from the string to the relative global variable (ActiveT,ActiveO..)
void set_conf_data(String cd);

// Error message: initiliazing library and MRKWAN module
void modem_start_err();

// Get modem info and display it(modem version, modem deviceEUI)
void info_modem();

// Error Message: Connection with gateway
void connect_to_gateway_message_error();

// Message successfully sent
void message_sent_ok();

// Message failed to send
void message_sent_error();

// Uplink Error Status
void uplink_error_status(int c, int e);

// Get number of a separator in a string 
String getValue(String data, char separator, int index);

// Get number of separators (used for integrity)
int countCheck(String data, char separator);

// Reset sensorsValues
void resetValues();

// Build uplink message string
String buildMSG(String lat,String lon);



/* Defining Functions */

String read_data_from_sensor() 
{
  String GPSValues[2] = {"-","-"}; //GPSValues will store Latitude and Longitude that we will get from the function readGPS() ((ADDED))

  if(sensorsActiveFlags[0]){
    sensorsValues[0] = random(0, 1000) / 100.0;
  }
  if(sensorsActiveFlags[1]){
    sensorsValues[1] = random(0, 1000) / 100.0;
  }
  if(sensorsActiveFlags[2]){
    sensorsValues[2] = random(0, 1000) / 100.0;
  }
  if(sensorsActiveFlags[3]){
    sensorsValues[3] = random(0, 1000) / 100.0;
  }
  if(sensorsActiveFlags[4] and sensorsActiveFlags[1] and sensorsActiveFlags[2] ){ //Benzene reliable read depends on having the temperature and humidity data, so if we skip Temp or Hum read, we also skip Benzene
    sensorsValues[4] = random(0, 100000) / 100.0;
  }
  if(sensorsActiveFlags[5]){
    sensorsValues[5] = random(0, 1000) / 100.0;
  }
  if(sensorsActiveFlags[6]){
    sensorsValues[6] = random(0, 1000) / 100.0;
  }
  if(sensorsActiveFlags[7]){
    GPSValues[0] = 45.6461391; //latitude
    GPSValues[1] = 9.5988159; //longitude
  }

  String msg = sensorsValues[0] + '|' + sensorsValues[1] + "|" +  sensorsValues[2] + "|" + sensorsValues[3] + "|" +  sensorsValues[4] + "|" +  sensorsValues[5] + "|" +  sensorsValues[6] + "|" + GPSValues[0] + "|" + GPSValues[1] + "|" + battery;
  //battery = battery - (((((double) rand() / (RAND_MAX)))+1)*0.25); //randomizza lo scaricamento tra -0.25 e -0.5
  battery = battery - (random(1000, 2000) / 100.0); // randomizza lo scaricamento tra float -10 e -20
  //battery = 45;
  resetValues();
  return msg;
}


int send_data_to_gateway(String msg)
{
  modem.beginPacket();
  modem.print(msg);
  return modem.endPacket(true);
}


int connect_to_gateway(String ae, String ak)
{
  return modem.joinOTAA(ae, ak); // connection and association with the gateway
}


String exchange_data_with_gateway()
{ 
  Serial.println();
  if (!modem.available()) //if there is no available data, return an empty string. 
  {
    Serial.print("No downlink message available at the moment...");
    return "";
  }
  //if some data is available...
  char rcv[64];
  int i = 0;
  while (modem.available()) 
  {
    rcv[i++] = (char)modem.read();
  }
  Serial.println("Received downlink message correctly..");
  String resultD = rcv; //convert char[64] to string  and return string received from the gateway (rcv)
  return resultD;
}


//DOWNLINK PARSING 
void set_conf_data_SIM(String data) 
{

  //variables for a robust downlink check
  int correctValues = 0; //variable for integrity check of downlink
  int newStates[9]; 
  
  delay(2500);
  if (data[0] == '1' or data[0] == '0' ){ // ---------------------- CONF TYPE DOWNLINK... WORKING 100% --------------------------------
    String part1 = ""; //Splitted String
    int seps = countCheck(data,'|'); //count separators
    if (seps == 9){
    for (int k = 0 ; k  <= seps; k++){  // for each "|" separator we divide in two 
      if (k < seps){
      part1 = data.substring(0,data.indexOf("|"));
      data = data.substring((data.indexOf("|") + 1));
      }
      else {
        part1 = data; //if it's the last iteraton of the parsing we only need to set part1 = data since we won't have another | "
      }
      //Serial.println(part1); //debug purposes
      //Serial.println(data); //debug purposes
  
      if (k < 8){
        if ((part1.toInt() == 1) or (part1.toInt() == 0)){
          correctValues++;
          newStates[k] = part1.toInt();
        } 
      }
      if (k == 8){
        if ((part1.toInt() > 10000) and (part1.toInt() < 200000)){
          correctValues++;
          newStates[k] = part1.toInt();
        }
      }
      if (k == 9) {
        if ((part1.toInt() > 10000) and (part1.toInt() < 200000)){
        correctValues++;
        newStates[k] = part1.toInt();
        }
      }
    }
    //Updating effective status of sensors
    if(correctValues == 10){
    for (int k = 0 ; k  <= seps; k++){
     if (k<8){
      sensorsActiveFlags[k] = newStates[k];
    }
    if (k==8){
      timetosend = newStates[k];
    }
    if (k==9) {
      timetoreceive = newStates[k];
    }
    }
    Serial.println("Downlink message accepted..");
    Serial.println("Sensors activated/deactivated as wanted..");
    return;
    
    }
    }
  }
  Serial.println("Invalid downlink message.. ");
  return;
}

void modem_start_err()
{
  Serial.println("Cannot start MRKWAN module, please retry.. ");
}

void info_modem()
{
  Serial.print("Your module version is: ");
  Serial.println(modem.version());
  Serial.print("EUI code of your device is: ");
  Serial.println(modem.deviceEUI());
}

void connect_to_gateway_message_error()
{
  Serial.println("Something went wrong; Are you indoor? Please move your Arduino board near a window and restart the script");
}

void message_sent_ok()
{
  Serial.println("Message successfully sent!");
}

void message_sent_error()
{
  Serial.println("Error sending the message...  ");
  Serial.println("Remember: You can send a limited number of message per minute, basing on your signal power!");
  Serial.println("Your signal power may range from 1 msg every few seconds to 1 msg per minute.");
}

void uplink_error_status(int c, int e)
{
  Serial.println("Uplink situation: ");
  delay(2000);
  Serial.println("Total cycles until now: " + c);
  Serial.println("Correct uplink message sent: " + (c-e));
  Serial.println("Errors " + e);
}

//countCheck will be rewritten in checkConfData
int countCheck(String data, char separator)
{
  int countSeparators = 0;
  for (int i = 0; i < data.length(); i++){
    if (data.charAt(i) == separator){ countSeparators ++; }
  }
  return countSeparators;
}

//resetValues: after each cycle it automatically resets the sensorsValues array.
void resetValues(){
  for (int i= 0; i < 7 ; i++){  //change 7
    sensorsValues[i] = "-";
  }
}


//buildMSG:
String buildMSG(String lat, String lon){
  String ms = ""; //initialize ms
  //Sensors - GPS
  for (int i = 0; i < 6 ;i++){  //change 6
    ms = ms + getSensInfos(i);
  }
  //GPS
  ms = ms + "Latitude:"+lat+"|"+"Longitude:"+lon+"|";
  //Battery
  ms = ms + "Battery:"+battery+"|";
  //other to add... power signal.. gateway communicating to..?
  Serial.println(ms);
  return ms;
}

#endif
/* IDEAS SECTION

Insert future upgrades here..

*/
