#include "Adafruit_MQTT.h"
#include "Adafruit_MQTT_Client.h"

#define MQTT_SERVER     "192.168.42.1"          // URL to the RPi running MQTT
#define MQTT_SERVERPORT 1883                    // MQTT service port
#define MQTT_USERNAME   ""                      // In preparation for securing the MQTT broker.
#define MQTT_PASSWORD   ""
#define MQTT_ID         "BPCUFFSENSOR-"         // Identifier to MQTT broker
#define SENSOR01_PUB	  "csec/device/bpcuff"    // Not accessible within Chatterbox, but through Pi mosquitto-clients

String                  ID        = "ID - ";
String                  mqttID( MQTT_ID );

////  Requires: '#include "WifiFunctions.h"' in main program
////  before:   '#include "MqttFunctions.h"'.
Adafruit_MQTT_Client    mqtt( &wifiClient, MQTT_SERVER, MQTT_SERVERPORT );
Adafruit_MQTT_Publish   devOutput = Adafruit_MQTT_Publish(   &mqtt, SENSOR01_PUB );

void MQTT_connect( int blockingTime )         // Function to connect and reconnect as necessary;
{ 
  int8_t rc;
  if ( mqtt.connected() )                     // If already connected...
  {
    mqtt.processPackets( blockingTime );
    if ( !mqtt.ping() )
      mqtt.disconnect();
  }
  else
  {
    Serial.println( "Connecting to MQTT..." );

    uint8_t retries = 15;
    while ( (rc = mqtt.connect()) != 0 )      // connect will return 0 for connected
    {
      Serial.println( mqtt.connectErrorString( rc ) );
      Serial.println( "Retrying MQTT connection in five seconds..." );
      mqtt.disconnect();
      delay( 5000 );                          // wait 5 seconds
      retries--;
      if ( retries == 0 ) 
        while ( true );     // Basically die and wait for WDT to reset.
    }
    Serial.println( "MQTT Connected." );
    Serial.print( "MQTT ID: " ); Serial.println( mqttID );
  }
}
