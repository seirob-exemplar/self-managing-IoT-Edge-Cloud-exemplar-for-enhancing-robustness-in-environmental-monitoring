#include <MKRWAN.h>
#include "arduino_secrets.h"
#include "functions.h"
#include "sensorsStates.h"


/* MODEM DECLARATION */
LoRaModem modem;

// Reading arduino_secrets.h values 
String appEui = SECRET_APP_EUI;
String appKey = SECRET_APP_KEY;

/* TEMPORAL TUNING VARIABLES DECLARATION */
unsigned long currentMillis;
unsigned long previousMillisS;
unsigned long previousMillisR;

/* RICONFIGURATION VARIABLES DECLARATION*/
String conf_data; //Configuration string received in the downlink process "1|1|1|1|1|1|1|1|20000|30000|40"
String msg; //Used for uplink

/* PERIOD VARIABLES DECLARATION */
int timetosend;
int timetoreceive;

/* OTHER VARIABLES DECLARATION*/
int cycle = 1;  //Just for debug purposes.
int lostPacket = 0; //Counts how many packets have not been transmitted from the watchdog to the gateway



/* SETUP FUNCTION - Initialization of Modem and Variables + Connection */
void setup() {
  
  Serial.begin(115200); 
  while (!Serial){
  if (!modem.begin(EU868)) {   // if initialization fails..
    modem_start_err(); 
    while (1) {}
  };
  info_modem();

  /* VARIABLES INITIALIZATION */
  timetosend = 20000; // ms
  timetoreceive = 40000; // ms
  previousMillisS = 0; // send 
  previousMillisR = 0; // data reception
  
  /* CONNECTION TO GATEWAY */
  int connected = 0; //set connected flag to false initially.. means we are offline.
  while (!connected){
    Serial.println("Arduino => Trying to connect with Gateway..");
    connected = connect_to_gateway(appEui, appKey); //we get 1 or 0 ... 1 means succesfully connected / 0 means we could not reach a gateway
    if (!connected) 
    {
      connect_to_gateway_message_error(); //print out error
      delay(60000); //we try to reconnect after 60 seconds, and we repeat this 'while' block of code.
    }
  }
  Serial.println("Arduino => Connected to gateway...."); //means we are online
  modem.minPollInterval(60);  // Set polling interval to 60 s 
  
  }
  
}



/* LOOP FUNCTION - */
void loop() { //read data from sensors --> msg --> conf-data

  currentMillis = millis(); // Assigning millis() value to variable 
  
  /* UPLINK DATA - PHASE 1 : READ FROM SENSORS */
  if( (unsigned long)(currentMillis-previousMillisS) >= timetosend )
  {
    Serial.println();
    Serial.println();
    Serial.println("----------------- CYCLE => " + String(cycle) + " -----------------" );
    String msg = read_data_from_sensor();
    Serial.println(msg); //String version 
    Serial.print("time to send: ");
    Serial.print(timetosend);
    Serial.print(" - time to receive: ");
    Serial.println(timetoreceive);
    cycle++; 
    
   /* UPLINK DATA - PHASE 2 : SEND DATA TO GATEWAY */
    int err = send_data_to_gateway(msg); //change to msg then
    if (err > 0)  // Check error code
    {
      message_sent_ok(); //message sent succesfully print 
    } 
    else 
    {
      message_sent_error(); //return error message
      lostPacket++; //increase error counter  
      delay(1500);
      uplink_error_status(cycle,lostPacket);
    }

    //to handle millis() rollover
    previousMillisS = currentMillis;
  }
  
  /* DOWNLINK DATA */
  if( (unsigned long)(currentMillis-previousMillisR) >= timetoreceive ) { 
   
    conf_data = exchange_data_with_gateway(); //See if there is a downlink msg available
    if(conf_data != "") // if conf_data is not empty
    {
      Serial.println(conf_data); //string to parse
      delay(1000);
      set_conf_data_SIM(conf_data);
    }

    //handle millis() rollover
    previousMillisR = currentMillis;
  }
     
}
