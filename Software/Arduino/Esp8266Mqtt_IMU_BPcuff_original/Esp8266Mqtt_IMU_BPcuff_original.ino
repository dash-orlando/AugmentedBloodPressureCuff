#include    "WifiFunctions.h"
#include    "MqttFunctions.h"
#include    "OtaFunctions.h"

/*Magnetometer global setup */
#include      <Wire.h>
#include      <SparkFunLSM9DS1.h>
#define       LSM9DS1_M             0x1E    // Would be 0x1C if SDO_M is LOW
#define       LSM9DS1_AG            0x6B    // Would be 0x6A if SDO_AG is LOW
#define       DECLINATION           6.3

#define       CAL_INDEX   50
#define       green       14
#define       red         13

LSM9DS1 imu;                          // Instantiate sensor.
double cal[3];
/*End Magnetometer global setup*/

void setup()
{
  /* Start up the serial port connection */
  Serial.begin( 115200 );
  while ( !Serial.available() ) ;

  /* Announce the title */
  Serial.println( "ESP8266 Mqtt IMU BP_Cuff Sensor" );

  /* Set up the WiFi as a station */
  WifiSetup();                                // Setup and connect to WiFi.

  /* Set up the callback service routines for MQTT subscriptions */
  //scenario.setCallback( scenarioCallback );   // Set up a 'Callback' function to service a subscription.
  //devInput.setCallback( devInputCallback );     // Set up a 'Callback' function to service another subscription.

  //mqtt.subscribe( &scenario );                // Now, subscribe to the topics for which Callbacks have been set up.
  //MQTT_connect( 100 );                        // Give MQTT enough time to receive the topic subscription.
  //mqtt.subscribe( &devInput );
  //MQTT_connect( 100 );

  /* Set up the OTA function */
  //if ( OTASetup() ) Serial.println( F("OTA Initialized") );
  //else Serial.println( F("OTA Initialization failed") );

  /* Just some info about system RAM; your code should go here... */
  Serial.print( "available memory: " ); 
  Serial.println( ESP.getFreeHeap() );

  /*Setup magnetometer for the main loop */
  Wire.begin();
  setupIMU();
  
  if ( !imu.begin() ) {
    Serial.print( F("Failed to communicate with LSM9DS1 ") );
    while (1);
  }

  pinMode(green, OUTPUT);                 //Enable the red and green LEDs
  pinMode(red, OUTPUT);

  for (int i = 0; i < CAL_INDEX; i++) {   //Zero the sensor.

    while ( !imu.magAvailable() );
    imu.readMag();

    cal[0] += imu.calcMag( imu.mx );
    cal[1] += imu.calcMag( imu.my );
    cal[2] += imu.calcMag( imu.mz );

    if ( i == CAL_INDEX - 1) {
      cal[0] = cal[0] / CAL_INDEX;
      cal[1] = cal[1] / CAL_INDEX;
      cal[2] = cal[2] / CAL_INDEX;
    };
  };

  Serial.println();
  Serial.println("Calibration values: ");   //Print out the calibration values.
  Serial.print("cal_x: ");
  Serial.print(cal[0]);
  Serial.print("\t");

  Serial.print("cal_y: ");
  Serial.print(cal[1]);
  Serial.print("\t");

  Serial.print("cal_z: ");
  Serial.print(cal[2]);
  Serial.println();
}


void loop()
{
  /* These need to be the first two lines in the loop() */
  //  ArduinoOTA.handle();                        // Check for OTA updates
  //  MQTT_connect( 100 );                        // Run the loop() at 1.25 Hz while MQTT blocks for 800ms
  /* Add user code below this line */
  double x, y, z, B;
  while ( !imu.magAvailable() );
  imu.readMag();
  x = double(imu.calcMag(imu.mx));
  y = double(imu.calcMag(imu.my));
  z = double(imu.calcMag(imu.mz));

  Serial.print(x - cal[0], 3);
  Serial.print(", ");
  Serial.print(y - cal[1], 3);
  Serial.print(", ");
  Serial.print(z - cal[2], 3);
  Serial.print("\t\t");
  Serial.print("Status: ");

  B = abs(pow( pow(x, 2.0) + pow(y, 2.0) + pow(z, 2.0), 0.5));
  if ( B < 1 ) {
    digitalWrite(red, LOW);
    digitalWrite(green, LOW);
    Serial.print("Out of Range");
  } else if ( B >= 5 ) {
    digitalWrite(green, HIGH);
    digitalWrite(red, LOW);
    Serial.print("Perfect\t");
  } else {
    digitalWrite(green, LOW);
    digitalWrite(red, HIGH);
    Serial.print("OK\t");
  };

  bool published = devOutput.publish(B);
  MQTT_connect(500);
  
  if ( published ) {
    Serial.print("\t\t");
    Serial.println("Successfully published.");
  } else {
    Serial.print("\t\t");
    Serial.println("Failed to publish.");
  };
}


void setupIMU() {
  imu.settings.device.commInterface = IMU_MODE_I2C; //
  imu.settings.device.mAddress      = LSM9DS1_M;    // Load IMU settings
  imu.settings.device.agAddress     = LSM9DS1_AG;   //

  imu.settings.gyro.enabled         = false;        // Enable gyro if true
  imu.settings.accel.enabled        = false;        // Enable accelerometer...
  imu.settings.mag.enabled          = true;         // Enable magnetometer...
  imu.settings.temp.enabled         = true;         // Enable temperature sensor...

  imu.settings.mag.scale            = 16;           // Set mag scale to +/-16 Gs
  imu.settings.mag.sampleRate       = 7;            // Set OD rate to 80Hz
  imu.settings.mag.tempCompensationEnable = true;   // Enable temperature compensation (good stuff!)

  imu.settings.mag.XYPerformance    = 3;            // 0 = Low || 1 = Medium || 2 = High || 3 = Ultra-high
  imu.settings.mag.ZPerformance     = 3;            // Ultra-high performance

  imu.settings.mag.lowPowerEnable   = false;        // Disable low power mode
  imu.settings.mag.operatingMode    = 0;            // 0 = Continuous || 1 = Single || 2 = OFF
}
