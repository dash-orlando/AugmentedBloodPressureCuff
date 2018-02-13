////#include <ESP8266mDNS.h>
////#include <WiFiUdp.h>
////#include <ESP8266httpUpdate.h>
//#include <ArduinoOTA.h>
//
//// ==================== OTA Setup ==================== //
///*                     ***********                     */
//String OTAErrorCode( int );
//
//boolean OTASetup()
//{
//  boolean result  = true;
//
//// Port defaults to 8266
//// ArduinoOTA.setPort(8266);
//
//// Hostname defaults to esp8266-[ChipID]
//  int str_len = mqttID.length() + 1;
//  char mqttID_charArray[str_len];
//  mqttID.toCharArray( mqttID_charArray, str_len );
//  ArduinoOTA.setHostname( mqttID_charArray );
//
//// No authentication by default
//// ArduinoOTA.setPassword( "admin" );
//// Password can be set with it's md5 value as well
//// MD5(admin) = 21232f297a57a5a743894a0e4a801fc3
//// ArduinoOTA.setPasswordHash( "21232f297a57a5a743894a0e4a801fc3" );
//
//  ArduinoOTA.onStart( []() 
//  {
//    String type;
//    if ( ArduinoOTA.getCommand() == U_FLASH )
//      type = "sketch";
//    else // U_SPIFFS
//      type = "filesystem";
//
//    // NOTE: if updating SPIFFS this would be the place to unmount SPIFFS using SPIFFS.end()
//    Serial.println( "Start updating " + type );
//  } );
//
//  ArduinoOTA.onEnd( []()
//  {
//    Serial.println( "\nEnd" );
//  } );
//
//  ArduinoOTA.onProgress( []( unsigned int progress, unsigned int total )
//  {
//    Serial.printf( "Progress: %u%%\r", (progress / (total / 100)) );
//  });
//
//  ArduinoOTA.onError( [&]( ota_error_t error )
//    {
//      result = false;
//      Serial.print( "Error.: " ); Serial.println( OTAErrorCode( error ) );
//      delay( 3000 );
//    } );
//
//  ArduinoOTA.begin();
//
//  return result;
//}
//
//
///* * * * * * * * * * * * * * * * * * * * * * * * * * * */
//// ============ OTA Error Codes Translator =========== //
///*             ****************************            */
//String OTAErrorCode( int n )
//{
//  String s = "";
//  switch ( n )
//  {
//    case OTA_AUTH_ERROR     : s = "OTA_AUTH_ERROR";     //   0
//    break;
//    case OTA_BEGIN_ERROR    : s = "OTA_BEGIN_ERROR";    //   1
//    break;
//    case OTA_CONNECT_ERROR  : s = "OTA_CONNECT_ERROR";  //   2
//    break;
//    case OTA_RECEIVE_ERROR  : s = "OTA_RECEIVE_ERROR";  //   3
//    break;
//    case OTA_END_ERROR      : s = "OTA_END_ERROR";      //   4
//    break;
//  }
//  return s;
//}

