''''
*
* CUSTOMIZED VERSION FOR DEMO PURPOSES
*
* GUI using appJar for Augmented Blood Pressure Cuff
*
* VERSION: 3.1.2
* 	- FIXED   : Sending commands to stethoscope now always works.
* 				( EVERYTHING failed earlier because logic
*				  statement was missing an equal = sign, lol )
*   - MODIFIED: Use the new stethoscopeDefinitions.
*   - ADDED   : Tried to understand Dani's code. Brain overload.
*               Could not compute!
*   - ADDED   : GUI is now in a class format.
*   - ADDED   : Integrated MQTT GUI with data from the BPCUFF Sensor
*
*
* KNOWN ISSUES:
*   - DANI!
*
* AUTHOR                    :   Mohammad Odeh
* DATE                      :   Nov. 15th, 2017 Year of Our Lord
* LAST CONTRIBUTION DATE    :   Aug.  8th, 2018 Year of Our Lord
*
* AUTHOR                    :   Edward Nichols
* DATE                      :   Feb. 18th, 2018 Year of Our Lord
* LAST CONTRIBUTION DATE    :   Feb. 20th, 2018 Year of Our Lord
*
'''

# Import the library
from    appJar                      import  gui                             # Import GUI
from    timeStamp                   import  fullStamp                       # Show date/time on console output
from    stethoscopeProtocol         import  *		                    	# Import all functions from the stethoscope protocol
from    stethoscopeDefinitions      import  *		                    	# Import all functions from the stethoscope definitions
from    bluetoothProtocol_teensy32  import  *		                    	# Import all functions from the bluetooth protocol -teensy3.2
from    threading                   import  Thread                          # Mulithreading
import  Queue                       as      qu
import  sys, time, bluetooth, serial, argparse, pexpect                     # 'nuff said

from    configurationProtocol       import  * 								# Determine stethoscope address based on device ID (MAC address)

class GUI(object):

    def __init__( self, logo, img, addr, MQTThost, MQTTtopic ):
        '''
        Create a GUI for interfacing Stethoscope and Blood Pressure Cuff.

        INPUTS:
            - logo : Absolute path to the pd3d logo as a string.
            - img  : Absolute path to the instructional image as a string.
            - addr : A list containing the mac addresses of stethoscopes.
        '''
        
        # Set MQTT attributes.
        self.MQTThost   = MQTThost
        self.MQTTtopic  = MQTTtopic

        # Initializing the object attributes to engage the playback of the audio on the stethoscope.
        self.pressureState  = False
        self.proximityState = False
        self.pitchState     = False
        self.rollState      = False
        self.playbackState  = False
        self.region         = 0
        self.region_old     = 0

        # Retrieve the size of the screen: (manually defined for now)
        # self.getScreenSize()
        self.pad        = 5
        self.resWidth   = 1280
        self.resHeight  = 800
        
        # Load image attributes.
        self.logo   = logo                                                  # Store logo as an attribute
        self.image  = img                                                   # Store image as an attribute
        
        # Create dictionary of subwindows, for easy referencing.
        self.subwindow = {  '1' : 'Embedded BP-CUFF Sensor Data',
                            '2' : 'DIAL PLACEHOLDER'         }

        # Store stethoscopes in a dictionary
        self.stt_addr = dict()                                              # Create empty dictionary
##        self.handle   = [None]*len(addr)                                    # Create empty list for handle name
        for i in range( len(addr) ):                                        # Loop over addresses 
            handle = "AS%03d" %(i+1)                                        # Construct handle
            self.stt_addr[ handle ] = addr[i]                               # Store into dictionary
        
        # ProceedS
        self.main()                                                         # Launch the main window

# ------------------------------------------------------------------------

    def main( self ):
        '''
        Create main window GUI for setup.
        '''

        # Predefined names for the sections/widgets of the window, in order of appearance.
        titleLabel = "title"
        
        cityloc = "City\t\t"
        steth   = "Steth.\t"
    
        logoLabel   = "pd3d_logo"
        startButton = "Start"
        quitButton1 = "Q1"
        
        ttl_name = "main_title"                                             # Title name
        lgo_name = "main_logo"                                              # Logo name
        
        # Set the parameters for the primary window:
        self.app = gui( "BPCUFF MQTT TEST v0.3.1" )                         # Create GUI variable
        self.app.setSize( "fullscreen" )                                    # Launch in fullscreen
        self.app.setBg( "black" )                                           # Set GLOBAL background color
        self.app.setFont( size=20 )                                         # Set GLOBAL font size

        ## Populating the primary window with labels and widgets:
        # Setup the title section: Row 0
        self.app.addLabel( ttl_name, "CSEC", colspan=2 )                    # Create a label
        self.app.setLabelBg( ttl_name, "gold" )                             # Set label's background color
        self.app.setLabelFg( ttl_name, "black" )                            # Set label's font color
        self.app.setPadding( [20, 20] )                                     # Pad outside the widgets

        # Setup the Location Selection section: Row 1
        # Add "Options Box"
        self.app.addLabelOptionBox( cityloc,                                # Create a dropdown menu for city
                                   [ "FL",                                  # ...
                                     "TX",                                  # ...
                                     "GA",                                  # Populate with cities
                                     "PA",                                  # ...
                                     "CA" ],                                # ...
                                     colspan=2 )                            # Fill entire span ( 2 columns)
        self.app.setLabelFg( cityloc, "gold" )                              # Set the color of 'City'
        self.app.setOptionBoxState( cityloc, "disabled" )

        # Setup the Stethoscope Selection section: Row 2
        # Add "Options Box"        
        self.app.addLabelOptionBox( steth,                                  # Create a dropdown menu for stethoscope
                                   [ "AS001" ],              				# ...
                                     colspan=2  )                           # Fill entire span
        self.app.setLabelFg( steth, "gold" )                                # Set the color of 'Stethoscope'
        self.app.setOptionBoxState( steth, "disabled" )

        # Setup the Stethoscope Selection section: Row 3
        # Add "Options Box"   
        self.app.addLabelOptionBox( "Mode  \t",                             # Create a dropdown menu for Modes
                                   [ "SIM",                                 # Populate with modes
                                     "REC" ],                               # ...
                                     colspan=2 )                            # Fill entire span
        self.app.setLabelFg( "Mode  \t", "gold" )                           # Set the color of 'Mode'
        self.app.setOptionBoxState( "Mode  \t", "disabled" )

        # Setup the Stethoscope Selection section: Row 4
        # Add PD3D logo image
        self.app.addImage( lgo_name, self.logo, colspan=2 )             


        # Setup the Stethoscope Selection section: Row 5
        # Add buttons and link them to actions.
        row = self.app.getRow()                                             # Get current row we are working on
        
        # Create buttons to interact with: Row
        self.app.setSticky("")
        self.app.addButton( startButton, self.MQTTwindow, row, 0, 1 )
        self.app.addNamedButton( "Quit", quitButton1, self.app.stop, row, 1, 1 )

        # Start GUI
        self.app.go()                                                       # Make window visible

# ------------------------------------------------------------------------

    def MQTTwindow(self, startButton_input):

            # Get values stored inside boxes
            self.stt = self.stt_addr[ self.app.getOptionBox( "Steth.\t" ) ]
            self.mde = self.app.getOptionBox( "Mode  \t" )

            # Predefined names for the sections/widgets of the subwindow.
            logotitle   = "logoastitle"
            proxLabel   = "prox"
            proxOut     = "proxOut"
            pitchLabel  = "pitch"
            pitchOut    = "pitchOut"
            rLabel      = "roll"
            rOut        = "rOut"
            connection  = "connection"
            quitButton2 = "Q2"
            
            if (startButton_input == "Start"):
                # Begin separate thread for the ABPC GUI in the background.
                self.app.thread( self.start_bpc )                         

                # Begin separate thread for MQTT.
                self.app.thread( self.MQTTupdate, proxOut, pitchOut, rOut, connection )

                # Begin separate thread for playing or disabling the audio on the stethoscope.
                self.app.thread( self.sttCommands)
                
                ## Set the parameters for the sub window: "MOSQUITTO Output"
                self.app.startSubWindow( self.subwindow['1'], modal=True )
                self.app.setBg( "black" )
                self.app.setPadding( [self.pad/2, self.pad/2] )
                self.app.setSize( (1*self.resWidth)/4, self.resHeight)
                self.app.setLocation( (3*self.resWidth)/4, 0)
                self.app.setFont(size=24)
                self.app.setSticky("nesw")
                self.app.setStretch("both")
                row = self.app.getRow()

               ## Populating the sub window with labels and widgets:
                 # Setup the Roll section: Row 0
                self.app.addLabel( logotitle, "CSEC", row, 0, colspan=3)
                self.app.setLabelBg( logotitle, "black" )
                self.app.setLabelFg( logotitle, "gold")
                row = row + 1

                # Setup the Roll section: Row 1
                self.app.addLabel( connection, "Awaiting MQTT... ", row, 0, colspan=3)
                self.app.setLabelBg( connection, "red" )
                self.app.setLabelFg( connection, "black")
                row = row + 1
                
                # Setup the Proximity section: Row 2
                self.app.addLabel( proxOut, "Proximity", row, 0, colspan=2 )
                self.app.setLabelBg( proxOut, "red")
                row = row + 1

                # Setup the Pitch section: Row 3
                self.app.addLabel( pitchOut, "Pitch", row, 0, colspan=2 )
                self.app.setLabelBg( pitchOut, "red")
                row = row + 1

                # Setup the Roll section: Row 4
                self.app.addLabel( rOut, "Roll", row, 0, colspan=2 )
                self.app.setLabelBg( rOut, "red")
                row = row + 1

                # Setup the Exit Button: Row 5
                self.app.setSticky("")
                self.app.addNamedButton( "Quit", quitButton2, self.app.stop, row, 0, colspan=2 )

                # Display the sub window!
                self.app.showSubWindow( self.subwindow['1'] )

            else:
                # Kill program and wonder in amazement.
                self.app.stop()
                Print("How is this even possible?")
        
# ------------------------------------------------------------------------

    def start_bpc( self ):
        '''
        Start Blood Pressure Cuff.
        '''
        
        # Print diagnostic information
        print( "Using Stethoscope %s with address %s"                       # Inform user which ...
               %(self.app.getOptionBox( "Steth.\t" ), self.stt) )           # ... stethoscope is used

        # Establish connection
        port = 1                                                            # Specify port to connect through
        self.stethoscope= createBTPort( self.stt, port )                    # Connect to device
        self.status     = statusEnquiry( self.stethoscope )                 # Send an enquiry byte

        if( self.status != 1 ):                                             # ...
            print( "Device reported back NAK. Troubleshoot device" )        # ...
            print( "Program will now exit." )                               # If the device reports back NAK
            closeBTPort( self.stethoscope )                                 # Kill everything
            time.sleep( 5.0 )                                               # ...
            self.app.stop()                                                 # ...

        else:
            pass

        print( "Launching BP Cuff Pressure Dial..." )
        # Construct command to pass to shell
        cmd = "python pressureDialGauge_v2.0.py --mode %s" %( self.mde )

        # Start BloodPressureCuff meter
        cuff = pexpect.spawn(cmd, timeout=None)                             # Spawn child

        for line in cuff:                                                   # Read STDOUT ...
            self.out = line.strip('\n\r')                                   # ... of spawned child ...
##            print( self.out )                                               # ... process and print.

            split_line = self.out.split(',')                                # Here is where we read pressure
            if( split_line[0] == "SIM" ):                                   # ABPC GUI has "SIM" printed ...
                self.region = int( split_line[1] )                          #   Get what region we are currently in
                
                if( self.region >= 0 ):                                     #   If we are in a simulation region
                    self.pressureState = True                               #   Set flag to true

                else:                                                       #   Else, set it to false
                    self.pressureState = False                              #   ...
                
        cuff.close()                                                        # Kill child process
        closeBTPort( self.stethoscope )                                     # Close BT connection
        
# ------------------------------------------------------------------------

    def MQTTupdate( self, proxOut, pitchOut, rOut, connection ):
            # Delay, to let the window come up!
            time.sleep( 3 )
            
            # Beginning the connection.
            initialState = True

            ## Using pexpect to interface with bash and linux mosquitto_clients.
            print( "Connecting to MQTT Client..." )
            mqttBash  	= "mosquitto_sub -h " + self.MQTThost + " -t " + self.MQTTtopic
            mqttClient 	= pexpect.spawn(mqttBash, timeout=None)

            #Loop forever, until program exit.
            while( True ): 
                # This is the same delay the Arduino program uses to publish to MQTT.
                # time.sleep(0.5)

                # Read a line from MQTT output in the terminal.
                # It is in format: "SENSORID,Hmag,pitch,roll,LOCATIONID" 
                mqttLine    = mqttClient.readline()
                mqttOutput  = mqttLine.split(",")

                if ( mqttOutput[0] == "BPCUFFSENS" ):
                    Hmag    = float( mqttOutput[1] )
                    pitch   = float( mqttOutput[2] )
                    roll    = float( mqttOutput[3] )
##                    print Hmag, pitch, abs(roll), self.proximityState, self.pressureState, self.playbackState

                    if (initialState == True):
                    # Update MQTT Connection Label, once connected.
                        self.app.queueFunction( self.app.setLabel(connection, "MQTT Connected") )
                        self.app.queueFunction( self.app.setLabelBg(connection, "green") )
                        initialState = False

                    ## Only update the window if and only if there was a state CHANGE:
                    # Proximity Label:
                    if (Hmag > 1.5):
                        if ( self.proximityState == False ):
                            # Previous state "NO", a change in state was observed.
                            # Update the proximity label to "OK"
                            self.app.queueFunction( self.app.setLabelBg(proxOut, "green") )
                            self.proximityState = True
                    else:
                        if ( self.proximityState == True ):
                            # Previous state "OK", a change in state was observed.
                            # Update the proximity label to "NO"
                            self.app.queueFunction( self.app.setLabelBg(proxOut, "red") )
                            self.proximityState = False

                    # Pitch Label:
                    if ( pitch < 80 and pitch >30 ):
                        if ( self.pitchState == False ):
                            # Previous state "NO", a change in state was observed.
                            # Update the pitch label to "OK"
                            self.app.queueFunction( self.app.setLabelBg(pitchOut, "green") )
                            self.pitchState = True
                    else:
                        if ( self.pitchState == True ):
                            # Previous state "OK", a change in state was observed.
                            # Update the proximity label to "NO"
                            self.app.queueFunction( self.app.setLabelBg(pitchOut, "red") )
                            self.pitchState = False

                    # Roll Label:
                    if ( abs(roll) < 30 ):
                        if ( self.rollState == False ):
                            # Previous state "NO", a change in state was observed.
                            # Update the roll label to "OK"
                            self.app.queueFunction( self.app.setLabelBg(rOut, "green") )
                            self.rollState = True
                    else:
                        if ( self.rollState == True ):
                            # Previous state "OK", a change in state was observed.
                            # Update the roll label to "NO"
                            self.app.queueFunction( self.app.setLabelBg(rOut, "red") )
                            self.rollState = False
                            
# ------------------------------------------------------------------------

    def sttCommands( self ):
        '''
        Loop to check the stethoscope audio playback conditions.
        '''

        blending = bool( False )                                            # Flag to indicate whther device is blending or not!
        time.sleep( 5 )                                                     # Delay to ensure BT connection was established

        while( True ):                                                      # Infinite loop
            time.sleep( 0.5 )         
##            print( self.proximityState, self.pressureState, self.playbackState )

            if( self.proximityState and self.pressureState ):               # Check conditions (magnet nearby & inside simulation interval)
            	if( self.region > 0 and not blending ): 					# 	If we are in SIM region & NOT blending
            			blendFileName = 'KOROT5'                            #       ...play this file.
                        matchIndex = blendByteMatching( blendFileName,      #       Search for appropriate byte within ...
                                                        blendFiles )        #       ... the array of available bytes.
                        fileByte = chr( blendInt[matchIndex] )              #       ... 
                        startBlending( self.stethoscope, fileByte )         #       Send the trigger command
                        blending = True                                     #       Set blending flag to True
            	
            	elif( self.region == 0 and blending ): 						# 	If we are in proximity but leave simulation region
            		stopBlending( self.stethoscope )                    	#       Stop blending
                    blending = False                                    	#       Set blending flag to False

            elif( self.proximityState == False or 							# If magnet is NOT nearby ...
            	  self.pressureState  == False ): 							# or if we are NOT inside simulation region
                if( blending ): 											#	If we are blending something
                	stopBlending( self.stethoscope )                    	#       Stop it because we shouldn't be augmenting
                    blending = False                                    	#       Set blending flag to False

##                if( self.region != self.region_old ):                       #   If we are in a different region than the previously captured one
##
##                    if  ( blending ):                                       #       Needed due to how stethoscope can NOT blend a file ...
##                        stopBlending( self.stethoscope )                    #       ... while it is already blending something else
##                        blending = False                                    #       Set blending flag to False
##                        
##                    if  ( self.region == 0 ):                               #       If we are not within simulation
##                        stopBlending( self.stethoscope )                    #       ... region, don't play anything
##                        blending = False                                    #       Set blending flag to False
##
##                    elif( self.region == 1 ):                               #       If we are within the 1st region
##                        blendFileName = 'KOROT4'                            #       ...play this file.
##                        matchIndex = blendByteMatching( blendFileName,      #       Search for appropriate byte within ...
##                                                        blendFiles )        #       ... the array of available bytes.
##                        fileByte = chr( blendInt[matchIndex] )              #       ... 
##                        startBlending( self.stethoscope, fileByte )         #       Send the trigger command
##                        blending = True                                     #       Set blending flag to True
##                        
##                    elif( self.region == 2 ):                               #       If we are within the 2nd region
##                        blendFileName = 'KOROT3'                            #       ...play this file.
##                        matchIndex = blendByteMatching( blendFileName,      #       Search for appropriate byte within ...
##                                                        blendFiles )        #       ... the array of available bytes.
##                        fileByte = chr( blendInt[matchIndex] )              #       ... 
##                        startBlending( self.stethoscope, fileByte )         #       Send the trigger command
##                        blending = True                                     #       Set blending flag to True
##
##                    elif( self.region == 3 ):                               #       If we are within the 3rd region
##                        blendFileName = 'KOROT2'                            #       ...play this file.
##                        matchIndex = blendByteMatching( blendFileName,      #       Search for appropriate byte within ...
##                                                        blendFiles )        #       ... the array of available bytes.
##                        fileByte = chr( blendInt[matchIndex] )              #       ... 
##                        startBlending( self.stethoscope, fileByte )         #       Send the trigger command
##                        blending = True                                     #       Set blending flag to True
##
##                    elif( self.region == 4 ):                               #       If we are within the 4th region
##                        blendFileName = 'KOROT1'                            #       ...play this file.
##                        matchIndex = blendByteMatching( blendFileName,      #       Search for appropriate byte within ...
##                                                        blendFiles )        #       ... the array of available bytes.
##                        fileByte = chr( blendInt[matchIndex] )              #       ... 
##                        startBlending( self.stethoscope, fileByte )         #       Send the trigger command
##                        blending = True                                     #       Set blending flag to True
##                        
##                    self.region_old = self.region                           #   Update flag

            else: pass
    
# ------------------------------------------------------------------------ 

# Define required parameters:
logo = "pd3d_inverted_with_title.gif"                                       # Logo name
img = "image.gif"                                                           # Image name

_, _, _, _, _, _, _, _, dataDir = definePaths()                             # Define directories for ...
panelID_list = dataDir + "/panels.txt"                                      # ... panel identification
_, _, panelID, _ = panelSelfID( panelID_list, getMAC("eth0") )              # Identify panel

deviceID_list = ("{}/panel{}devices.txt").format(dataDir, panelID)          # Define directories for device identification
_, _, bt_address_list = panelDeviceID( deviceID_list, panelID )

sttaddr = [ bt_address_list[0] ]                                            # Get stethoscope address

mqtthost  = "192.168.42.1"
mqtttopic = "csec/device/bpcuff_1"

# START!
display = GUI( logo, img, sttaddr, mqtthost, mqtttopic )
