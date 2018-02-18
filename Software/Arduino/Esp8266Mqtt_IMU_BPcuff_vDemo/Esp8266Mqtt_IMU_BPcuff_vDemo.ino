/*
   Built off of Michael Xynidis' ESP8266 Template.
   Obtain magnetic field and acceleration vectors from IMU.
   Obtained values take into account the magnetic field of the earth.
   The magnitude of the magnetic field monitors the proximity of a magnet embedded on the stethoscope.
   The pitch, roll derived with the addition of the accelerometer data monitors the orientation of the BP cuff.
   A string compiled from the values of B, pitch, roll, and status is published through to an mqtt broker.

   AUTHOR                  : Edward Daniel Nichols
   LAST CONTRIBUTION DATE  : Feb 17th, 2018, Year of Our Lord

   CHANGELOG:-
    1- New functions were defined to make the calculation of values simpler.
    2- Full reporting to MQTT was implemented.
    3- The speed of publishing to MQTT was significantly improved.
    4- Orientation check feature (from roll) was included at Fluvio's request.
    5- Output condensed and encoded for integration with Python GUI scripts.
*/

/*Required local libraries: IN THIS ORDER */
#include    "WifiFunctions.h"
#include    "MqttFunctions.h"

/*Magnetometer global setup: header library files. */
#include   <Wire.h>
#include   <SparkFunLSM9DS1.h>

/*Magnetometer global setup: static definitions. */
#define     LSM9DS1_M             0x1E    // Would be 0x1C if SDO_M is LOW.
#define     LSM9DS1_AG            0x6B    // Would be 0x6A if SDO_AG is LOW.
#define     DECLINATION           6.3     // Geomagnetic field effect on 12/14/17 in Oviedo, FL.
#define     CAL_INDEX             50      // Number of initial readings to average over for calibration.
#define     MAGNET                14      // Output pin tied to an LED indicating the state of proximity;   HIGH --> OK state.
#define     ORIENTATION           13      // Output pin tied to an LED indicating the state of orientation; HIGH --> OK state.

LSM9DS1 imu;                              // Instantiate sensor.
double  H, roll, pitch;                   // Values of interest.
String  article, serialStr;               // String object to aggregate output for publishing.

void setup()
{
  // Start up the serial port connection and announce title.
  Serial.begin( 115200 );
  Serial.println( "ESP8266 Mqtt IMU BP_Cuff Sensor" );

  WifiSetup();                                // Setup and connect to WiFi.
  setupIMU();                                 // Set IMU operation parameters.

  if ( !imu.begin() ) {
    // If the sensor fails to communicate with the IMU, it will redo the setup function.
    Serial.print( F("Failed to communicate with LSM9DS1 ") );
    setup();
  };

  // Prompt MQTT to connect for the first time.
  MQTT_connect( 250 );
}


void loop()
{

  // Calculate the values of interest. [See function definitions below.]
  calcH();
  calcAttitude();

  // Prepare string to publish to the Serial Bus.
  serialStr = String("H: "); serialStr.concat(H); 
  serialStr.concat("\nPitch: "); serialStr.concat(pitch);
  serialStr.concat("\nRoll: "); serialStr.concat(roll);
  serialStr.concat("\n");
  Serial.println(serialStr);

  // Prepare string to publish the values to MQTT
  article = String("BPCUFFSENS,");
  article.concat(H); article.concat(",");
  article.concat(pitch); article.concat(",");
  article.concat(roll); article.concat(",PD3D");
  
  // Verify MQTT broker is connected.
  if ( !mqtt.connected() )
    MQTT_connect(500);

  // Convert the String object to a character array, so that MQTT can actually publish it. */
  char post[64];
  article.toCharArray(post, 64);
  devOutput.publish(post);

  // Delay to give MQTT time to catch up.
  delay(500);
};


void calcH() {
  float now_mx, now_my, now_mz;
  while ( !imu.magAvailable() );
  imu.readMag();

  now_mx = -1 * float(imu.calcMag(imu.my));
  now_my = -1 * float(imu.calcMag(imu.mx));
  now_mz = float(imu.calcMag(imu.mz));

  // H is a global variable, representing the magnitude of the magnetic field.
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

  // Roll is a global variable.
  roll    = float( atan2(now_ay, now_az) );
  roll   *= 180.0 / PI;

  // Pitch is a global variable.
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
