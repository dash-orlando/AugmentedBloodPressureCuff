#include  <ESP8266WiFi.h>

#define   WLAN_SSID "pd3d"
#define   WLAN_PASS "n3w.pas."

enum        State         { CONNECTED, DISCONNECTED };
boolean     wifiState;

uint8_t     MAC_init[]    = {0,0,0,0,0,0};
uint8_t     MAC_array[6];
char        MAC_char[18];

WiFiClient  wifiClient;

String WiFiErrorCode( int );  // Forward declaration

/* * * * * * * * * * * * * * * * * * * * * * * * * * * */
// ==================== WiFi Setup =================== //
/*                     ************                    */
boolean WifiSetup()
{
  boolean wifiFail  = false;
  int     cnt       =  0;

  wifiState         = DISCONNECTED;   // work with this a little later to remove wifiFail
  
  WiFi.mode( WIFI_STA );
  WiFi.begin( WLAN_SSID, WLAN_PASS );
  Serial.println( "Connecting to WiFi..." );
  Serial.println( WiFiErrorCode( WiFi.status() ) );
  while ( ( WiFi.status() != WL_CONNECTED ) && ( !wifiFail ) )
  {
    Serial.print( "." );
    delay( 500 );
    if ( ++cnt % 20 == 0 ) Serial.println();
    if ( cnt == 40 )  // 40 for 20 seconds
    {
      int s = WiFi.status();
      Serial.print( "WiFi status = " ); Serial.println( WiFiErrorCode( s ) );
      wifiFail = true;
//      while ( true ) ;                // loop forever and wait for reset or wdt
    }
  }
  if ( wifiFail )
  {
    wifiState = DISCONNECTED;
  }
  else
  {
    Serial.println( "\nConnected to WiFi." );
    Serial.print( "IP: " );
    Serial.println( WiFi.localIP() );

    uint8_t* MAC  = WiFi.macAddress( MAC_init );
    for ( int i = 2; i < 15; i += 3 ) MAC_char[i] = ':';
    for ( int i = 0, j = 0; i < 17; i += 3, j++ )
    {
      MAC_char[i]   = (MAC[j] & 0xF0) >> 4;
      MAC_char[i+1] = MAC[j] & 0x0F;
      if ( MAC_char[i] > 0x09 ) MAC_char[i] += 0x37; else MAC_char[i] += 0x30;
      if ( MAC_char[i+1] > 0x09 ) MAC_char[i+1] += 0x37; else MAC_char[i+1] += 0x30;
    }
    MAC_char[17] = '\0';
    Serial.printf( "MAC: %s\n", MAC_char );   
    
    wifiState = CONNECTED;
  }
    Serial.println( WiFiErrorCode( WiFi.status() ) );
  return !wifiFail;
} //*/


/* * * * * * * * * * * * * * * * * * * * * * * * * * * */
// =========== WiFi Error Codes Translator =========== //
/*            *****************************            */
String WiFiErrorCode( int n )
{
  String s = "";
  switch ( n )
  {
    case WL_IDLE_STATUS     : s = "WL_IDLE_STATUS";     //   0
    break;
    case WL_NO_SSID_AVAIL   : s = "WL_NO_SSID_AVAIL";   //   1
    break;
    case WL_SCAN_COMPLETED  : s = "WL_SCAN_COMPLETED";  //   2
    break;
    case WL_CONNECTED       : s = "WL_CONNECTED";       //   3
    break;
    case WL_CONNECT_FAILED  : s = "WL_CONNECT_FAILED";  //   4
    break;
    case WL_CONNECTION_LOST : s = "WL_CONNECTION_LOST"; //   5
    break;
    case WL_DISCONNECTED    : s = "WL_DISCONNECTED";    //   6
    break;
    case WL_NO_SHIELD       : s = "WL_NO_SHIELD";       // 255
    break;
  }
  return s;
}

