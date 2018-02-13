/*
   Built off of Michael Xynidis' ESP8266 Template.
   Obtain magnetic field and acceleration vectors from IMU.
   Obtained values take into account the magnetic field of the earth.
   The magnitude of the magnetic field monitors the proximity of a magnet embedded on the stethoscope.
   The pitch, roll derived with the addition of the accelerometer data monitors the orientation of the BP cuff.
   A string compiled from the values of B, pitch, roll, and status is published through to an mqtt broker.

   AUTHOR                  : Edward Daniel Nichols
   LAST CONTRIBUTION DATE  : Dec. 14th, 2017, Year of Our Lord

   CHANGELOG:-
    1- New functions were defined to make the calculation of values simpler.
    2- Full reporting to MQTT was implemented.
    3- The speed of publishing to MQTT was significantly improved.
    4- Orientation check feature (from roll) was included at Fluvio's request.
*/

/*Required local libraries */
#include    "WifiFunctions.h"
#include    "MqttFunctions.h"
#include    "OtaFunctions.h"

/*Magnetometer global setup */
#include   <Wire.h>
#include   <SparkFunLSM9DS1.h>

#define     LSM9DS1_M             0x1E    // Would be 0x1C if SDO_M is LOW
#define     LSM9DS1_AG            0x6B    // Would be 0x6A if SDO_AG is LOW
#define     DECLINATION           6.3     // Geomagnetic field effect on 12/14/17 in Oviedo, FL
#define     CAL_INDEX             50
#define     MAGNET                14
#define     ORIENTATION           13

LSM9DS1 imu;                          // Instantiate sensor.
double  H, roll, pitch;
/*End Magnetometer global setup*/

String  article;                      // String object to aggregate output for publishing.

void setup()
{
  /* Start up the serial port connection and announce title */
  Serial.begin( 115200 );
  Serial.println( "ESP8266 Mqtt IMU BP_Cuff Sensor" );

  /* Set up the WiFi as a station */
  WifiSetup();                                // Setup and connect to WiFi.

  /* SEE DEPRECATED CODE: 1 */

  /* Setup magnetometer for the main loop */
  setupIMU();

  if ( !imu.begin() ) {
    Serial.print( F("Failed to communicate with LSM9DS1 ") );
    setup();
  };

  /* Enable the LEDs for visual cues */
  pinMode(MAGNET, OUTPUT);                         //Enable the red and green LEDs
  pinMode(ORIENTATION, OUTPUT);

  /* Connect to the MQTT broker */
  MQTT_connect( 250 );
}


void loop()
{
  /* SEE DEPRECATED CODE: 2 */

  /* Calculate the values of interest.
     [See function definitions below.] */
  calcH();
  calcAttitude();

  /* Print the values to the Serial Bus. */
  Serial.print("H mag: ");
  Serial.print(H, 2);
  Serial.print("\t");

  Serial.print("Pitch: ");
  Serial.print(pitch, 2);
  Serial.print("\t");

  Serial.print("Roll: ");
  Serial.print(roll, 2);
  Serial.println();

  /* Append the raw values, and formatting, to the article for publishing. */
  article = String("\nH:\t");
  article.concat(H);
  article.concat("\n");

  article.concat("pitch:\t");
  article.concat(pitch);
  article.concat("\n");

  article.concat("roll:\t");
  article.concat(roll);
  article.concat("\n");

  /* Append to string conditionally.
     If the proximity of the stethoscope (magnet) is acceptable,
     prepare to publish an OK. */
  article.concat("Scope Proximity: \t");
  if (H > 6) {
    digitalWrite(MAGNET, HIGH);
    article.concat("OK\n");
  } else {
    digitalWrite(MAGNET, LOW);
    article.concat("\n");
  };

  /* Append to string conditionally.
   *  If the orientation is acceptable,
      prepare to publish an OK. */
  article.concat("Cuff Orientation: \t");
  if (abs(roll) < 80) {
    digitalWrite(ORIENTATION, HIGH);
    article.concat("OK\n");
  } else {
    digitalWrite(ORIENTATION, LOW);
    article.concat("\n");
  };

  /* Verify MQTT broker is connected. */
  if ( !mqtt.connected() )
    MQTT_connect(500);

  /* Convert the String object to a character array, so that MQTT can actually publish it. */
  char post[82];
  article.toCharArray(post, 82);
  devOutput.publish(post);

  /* Delay to give MQTT time to catch up:
     Value of about 200ms to 250ms is sufficient to maintain real-time throughput to screen via Chatterbox.
  */
  delay(1000);
};


void calcH() {
  float now_mx, now_my, now_mz;
  while ( !imu.magAvailable() );
  imu.readMag();

  now_mx = -1 * float(imu.calcMag(imu.my));
  now_my = -1 * float(imu.calcMag(imu.mx));
  now_mz = float(imu.calcMag(imu.mz));

  /* H is a global variable, representing the magnitude of the magnetic field. */
  H = abs(pow( pow(now_mx, 2.0) + pow(now_my, 2.0) + pow(now_mz, 2.0), 0.5));
};


void calcAttitude()
{
  float now_ax, now_ay, now_az;
  while ( !imu.accelAvailable());
  imu.readAccel();

  now_ax = float(imu.calcAccel(imu.ax));
  now_ay = float(imu.calcAccel(imu.ay));
  now_az = float(imu.calcAccel(imu.az));

  /* roll is a global variable */
  roll    = float( atan2(now_ay, now_az) );
  roll   *= 180.0 / PI;

  /* pitch is a global variable */
  pitch   = float( atan2(-now_ax, sqrt(now_ay * now_ay + now_az * now_az)) );
  pitch  *= 180.0 / PI;
};


void setupIMU() {
  imu.settings.device.commInterface = IMU_MODE_I2C; //
  imu.settings.device.mAddress      = LSM9DS1_M;    // Load IMU settings
  imu.settings.device.agAddress     = LSM9DS1_AG;   //

  imu.settings.gyro.enabled         = false;        // Enable gyro if true
  imu.settings.accel.enabled        = true;         // Enable accelerometer...
  imu.settings.mag.enabled          = true;         // Enable magnetometer...
  imu.settings.temp.enabled         = true;         // Enable temperature sensor...
};


/* DEPRECATED CODE 1 */
//scenario.setCallback( scenarioCallback );   // Set up a 'Callback' function to service a subscription.
//devInput.setCallback( devInputCallback );     // Set up a 'Callback' function to service another subscription.

//mqtt.subscribe( &scenario );                // Now, subscribe to the topics for which Callbacks have been set up.
//MQTT_connect( 100 );                        // Give MQTT enough time to receive the topic subscription.
//mqtt.subscribe( &devInput );
//MQTT_connect( 100 );

/* Set up the OTA function */
//if ( OTASetup() ) Serial.println( F("OTA Initialized") );
//else Serial.println( F("OTA Initialization failed") );

/* Info about system RAM */
//Serial.print( "available memory: " );
//Serial.println( ESP.getFreeHeap() );


/* DEPRECATED CODE 2 */
//  ArduinoOTA.handle();                        // Check for OTA updates [Uncomment to enable]
//  MQTT_connect( 100 );                        // Do I even need one of these?
