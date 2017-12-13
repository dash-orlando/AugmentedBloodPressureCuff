#include "Adafruit_MQTT.h"
#include "Adafruit_MQTT_Client.h"
#include "SubscriptionCallbacks.h"

#define MQTT_SERVER     "192.168.42.1"        // URL to the RPi running MQTT
#define MQTT_SERVERPORT 1883                  // MQTT service port
#define MQTT_USERNAME   ""
#define MQTT_PASSWORD   ""
#define MQTT_ID         "BPCUFFSENSOR-"        // Identifier to MQTT broker

#define SCENARIO_SUB	  "csec/simulation/exam/scenario/sub"
#define SENSOR01_SUB	  "csec/device/bpcuff/sub"
#define SENSOR01_PUB	  "pd3d/test/sample"     //This should be csec/device/bpcuff_sensor/pub for the BP cuff proximity sensor

String                  ID        = "ID - ";
String                  mqttID( MQTT_ID );


////  Requires: '#include "WifiFunctions.h"' in main program
////  before:   '#include "MqttFunctions.h"'.
Adafruit_MQTT_Client    mqtt( &wifiClient, MQTT_SERVER, MQTT_SERVERPORT );

//Adafruit_MQTT_Subscribe scenario  = Adafruit_MQTT_Subscribe( &mqtt, SCENARIO_SUB );
//Adafruit_MQTT_Subscribe devInput  = Adafruit_MQTT_Subscribe( &mqtt, SENSOR01_SUB );
Adafruit_MQTT_Publish   devOutput = Adafruit_MQTT_Publish(   &mqtt, SENSOR01_PUB );


String lookupID( String mac )
{
  String s = "";
  if (      mac == "60:01:94:14:E4:00" ) s = "01";
  else if ( mac == "60:01:94:14:DC:89" ) s = "02";
  else if ( mac == "A0:20:A6:36:6F:7F" ) s = "03";
  else Serial.println( "unlisted MAC" );
  mqttID.concat( s );
  ID.concat( s );
  return s;
}

void MQTT_connect( int blockingTime )         // Function to connect and reconnect as necessary;
{                                             // ...run from loop()
  int8_t rc;

  if ( mqtt.connected() )                     // If already connected...
  {
    mqtt.processPackets( blockingTime );
    if( !mqtt.ping() ) mqtt.disconnect();
  }
  else
  {
    Serial.println( "Connecting to MQTT..." );
  
    uint8_t retries = 3;
    while ( (rc = mqtt.connect()) != 0 )      // connect will return 0 for connected
    {
      Serial.println( mqtt.connectErrorString( rc ) );
      Serial.println( "Retrying MQTT connection in five seconds..." );
      mqtt.disconnect();
      delay( 5000 );                          // wait 5 seconds
      retries--;
      if ( retries == 0 ) while ( true );     // Basically die and wait for WDT to reset.
    }
    Serial.println( "MQTT Connected." );
    lookupID( MAC_char );

    Serial.print( "MQTT ID: " ); Serial.println( mqttID );
  }
}
