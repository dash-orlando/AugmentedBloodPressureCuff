'''
*
* PRELIMINARY SETUP FOR DEMO
* THIS IS A TEST BEFORE INTEGRATION
*
* GUI using appJar for Augmented Blood Pressure Cuff
*
* VERSION: 0.2.6.BETA
*
*
* AUTHOR                    :   Edward Nichols
* DATE                      :   Feb. 17th, 2018 Year of Our Lord
* LAST CONTRIBUTION DATE    :   Feb. 18th, 2018 Year of Our Lord
'''

from    appJar           import     gui          
from    timeStamp        import     fullStamp
from    threading        import     Thread
from    time             import     sleep
import  Queue            as         qu
import  paho.mqtt.client as         mqtt
import  pexpect          as         bash

### Required parameters:
mqtthost = "192.168.42.1"
mqttport = 1883   
logo = "pd3d_inverted_with_title.gif"

class GUI(object):

    ### Function 0: Initialization
    def __init__(self, logo_location, MQTThost, MQTTtopic ):

        ## Setting useful object attributes and parameters for the GUI: 
        # Create dictionary of subwindows.
        self.subwindow = {  '1' : 'Embedded BP-CUFF Sensor',
                            '2' : 'DIAL PLACEHOLDER'         }

        # Set object attributes.
        self.logo = logo_location
        self.MQTThost = MQTThost
        self.MQTTtopic = MQTTtopic

        # Predefined names for the sections/widgets of the window.
        titleLabel = "title"
        logoLabel = "pd3d_logo"
        startButton = "Start"
        quitButton1 = "Q1"

        # Retrieve the size of the screen: (manually defined for now)
        # self.getScreenSize()
        self.pad = 10
        self.resWidth = 1980
        self.resHeight = 1080
        
        # Set the parameters for the primary window:
        self.main = gui( "BPCUFF MQTT TEST v0.2.7")
        self.main.setSize( self.resWidth/4-6*self.pad, self.resHeight-2*self.pad)
        self.main.setLocation( 3*(self.resWidth/4), 0 )
        self.main.setBg("black")
        self.main.setFont(size=36)
        self.main.setPadding( [self.pad, self.pad] )
        self.main.setSticky("ew")

        ## Populating the primary window with labels and widgets:
        # Setup the title section: Row 0
        self.main.addLabel( titleLabel, "CSEC", 0, 0, 2)
        self.main.setLabelBg( titleLabel, "gold")
        self.main.setLabelFg( titleLabel, "black")

        # Setup the logo section: Row 1
        self.main.addImage( logoLabel, self.logo, 1, 0, 2)

        # Create buttons to interact with: Row 2
        self.main.setSticky("")
        self.main.addButton( startButton, self.MQTTwindow, 2, 0, 1 )
        self.main.addNamedButton( "Quit", quitButton1, self.main.stop, 2, 1, 1 )

        # Start the GUI
        self.main.go()

    ### Function 1: Sub-Window Concept Function, to integrate with demo GUI.
    def MQTTwindow(self, startButton_input):

        # Predefined names for the sections/widgets of the subwindow.
        logotitle = "logoastitle"
        proxLabel = "prox"
        proxOut = "proxOut"
        pitchLabel = "pitch"
        pitchOut = "pitchOut"
        rLabel = "roll"
        rOut = "rOut"
        connection = "mqttconnect"
        quitButton2 = "Q2"
        
        if (startButton_input == "Start"):
            # Begin separate thread for MQTT.
            self.main.thread( self.MQTTupdate, proxOut, pitchOut, rOut, connection )
            
            ## Set the parameters for the sub window: "MOSQUITTO Output"
            self.main.startSubWindow( self.subwindow['1'], modal=True )
            self.main.setBg( "black" )
            self.main.setPadding( [self.pad/2, self.pad/2] )
            self.main.setSize( self.resWidth/4-6*self.pad , self.resHeight-2*self.pad)
            self.main.setLocation( (3*self.resWidth)/4, 0 )
            self.main.setFont(size=36)
            self.main.setSticky("nesw")
            self.main.setStretch("both")
            row = self.main.getRow()

            ## Populating the sub window with labels and widgets:
            # Setup the title section: Row 0
            self.main.addImage( logotitle, self.logo, 0, 0, colspan=3)
            row = row + 1
            
            # Setup the Proximity section: Row 1
            self.main.setFont(size=24)
            self.main.addLabel( proxLabel, "Proximity: ", row, 0, colspan=1)
            self.main.setLabelBg( proxLabel, "gold" )
            self.main.setLabelFg( proxLabel, "black")

            self.main.addLabel( proxOut, "\t\tNO\t", row, 1, colspan=2 )
            self.main.setLabelBg( proxOut, "red")
            row = row + 1

            # Setup the Pitch section: Row 2
            self.main.addLabel( pitchLabel, "Pitch: ", row, 0, colspan=1)
            self.main.setLabelBg( pitchLabel, "gold" )
            self.main.setLabelFg( pitchLabel, "black")

            self.main.addLabel( pitchOut, "\t\tNO\t", row, 1, colspan=2 )
            self.main.setLabelBg( pitchOut, "red")
            row = row + 1

            # Setup the Roll section: Row 3
            self.main.addLabel( rLabel, "Roll: ", row, 0, colspan=1)
            self.main.setLabelBg( rLabel, "gold" )
            self.main.setLabelFg( rLabel, "black")

            self.main.addLabel( rOut, "\t\tNO\t", row, 1, colspan=2 )
            self.main.setLabelBg( rOut, "red")
            row = row + 1

            # Setup the Roll section: Row 4
            self.main.addLabel( connection, "Awaiting Connection... ", row, 0, colspan=3)
            self.main.setLabelBg( connection, "red" )
            self.main.setLabelFg( connection, "black")
            row = row + 1

            # Setup the Exit Button: Row 5
            self.main.setSticky("")
            self.main.addNamedButton( "Quit", quitButton2, self.main.stop, row, 0, colspan=3 )

            # Display the sub window!
            self.main.showSubWindow( self.subwindow['1'] )

        else:
            self.main.stop()
            Print("How is this even possible?")

    ### Function 2: The MQTT update function, to run on a thread within F1.
    def MQTTupdate(self, proxOut, pitchOut, rOut, connection):
        # Delay, to let the window come up!
        sleep(2.5)
        
        ## Make room to save some historical data, to enable the evaluation of state changes.
        startState = True
        stateHmag = False
        statePitch= False
        stateRoll = False

        ## Using pexpect to interface with bash and linux mosquitto_clients.
        print("Connecting to MQTT Client...")
        mqttBash = "mosquitto_sub -h " + self.MQTThost + " -t " + self.MQTTtopic
        mqttClient = bash.spawn(mqttBash, timeout=None)

        #Loop forever, until program exit.
        while(True): 
            # This is the same delay the Arduino program uses to publish to MQTT.
            # sleep(0.5)

            # Read a line from MQTT output in the terminal.
            # It is in format: "SENSORID,Hmag,pitch,roll,LOCATIONID" 
            mqttLine = mqttClient.readline()
            mqttOutput = mqttLine.split(",")

            if (mqttOutput[0] == "BPCUFFSENS" ):
                Hmag = float(mqttOutput[1])
                pitch = float(mqttOutput[2])
                roll = float(mqttOutput[3])
                print Hmag, pitch, abs(roll), stateHmag, statePitch, stateRoll

                if (startState == True):
                    # Update MQTT Connection Label, once connected.
                    self.main.queueFunction( self.main.setLabel(connection, "MQTT Connected.") )
                    self.main.queueFunction( self.main.setLabelBg(connection, "green") )
                    startState = False

                ## Only update the window if and only if there was a state CHANGE:
                # Proximity Label:
                if (Hmag > 5.0):
                    if (stateHmag == False):
                        # Previous state "NO", a change in state was observed.
                        # Update the proximity label to "OK"
                        self.main.queueFunction( self.main.setLabel(proxOut, "\tOK\t\t\t") )
                        self.main.queueFunction( self.main.setLabelBg(proxOut, "green") )
                        stateHmag = True
                else:
                    if (stateHmag == True):
                        # Previous state "OK", a change in state was observed.
                        # Update the proximity label to "NO"
                        self.main.queueFunction( self.main.setLabel(proxOut, "\t\tNO\t") )
                        self.main.queueFunction( self.main.setLabelBg(proxOut, "red") )
                        stateHmag = False

                # Pitch Label:
                if ( pitch > 25.0 ):
                    if (statePitch == False):
                        # Previous state "NO", a change in state was observed.
                        # Update the pitch label to "OK"
                        self.main.queueFunction( self.main.setLabel(pitchOut, "\tOK\t\t\t") )
                        self.main.queueFunction( self.main.setLabelBg(pitchOut, "green") )
                        statePitch = True
                else:
                    if (statePitch == True):
                        # Previous state "OK", a change in state was observed.
                        # Update the proximity label to "NO"
                        self.main.queueFunction( self.main.setLabel(pitchOut, "\t\tNO\t") )
                        self.main.queueFunction( self.main.setLabelBg(pitchOut, "red") )
                        statePitch = False

                # Roll Label:
                if ( abs(roll) > 90.0 ):
                    if (stateRoll == False):
                        # Previous state "NO", a change in state was observed.
                        # Update the roll label to "OK"
                        self.main.queueFunction( self.main.setLabel(rOut, "\tOK\t\t\t") )
                        self.main.queueFunction( self.main.setLabelBg(rOut, "green") )
                        stateRoll = True
                else:
                    if (stateRoll == True):
                        # Previous state "OK", a change in state was observed.
                        # Update the roll label to "NO"
                        self.main.queueFunction( self.main.setLabel(rOut, "\t\tNO\t") )
                        self.main.queueFunction( self.main.setLabelBg(rOut, "red") )
                        stateRoll = False          
        
    ### Function 3: Find and set screen resolution attributes dynamically, for GUI adpatability!
    ### Not working! 
    def getScreenSize (self):
        # It uses PyQt4, which interrupts appJar for some reason.
        # I figure we can run this independently and retrieve the values.

        # Should be in the same directory as this python script!
        screenScript = "python screenRes.py"

        # The script outputs width and height on same line, but there's some funky character stuff I can't seem to get rid of.
        screenSize = pexpect.spawn( screenScript, timeout=None )

        output = screenSize.read()
        print(output)
    
       
### Run the program:
host = "192.168.42.1"
topic = "csec/device/bpcuff"
display = GUI(logo, host, topic)
