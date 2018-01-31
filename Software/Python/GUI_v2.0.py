'''
*
* GUI using appJar for Augmented Blood Pressure Cuff
*
* VERSION: 0.2
*   - ADDED   : Specify what sound type is being recorded
*   - MODIFIED: String format is changed to be compatible with stethoscope's format
*
* KNOWN ISSUES:
*   - None atm
*
* AUTHOR                    :   Mohammad Odeh
* DATE                      :   Nov. 15th, 2017 Year of Our Lord
* LAST CONTRIBUTION DATE    :   Nov. 01st, 2017 Year of Our Lord
*
'''

# Import the library
from    appJar                  import gui                  # Import GUI
from    timeStamp               import fullStamp            # Show date/time on console output
#import  pressureDialGauge_GUI                               # Import pressureDialGauge
import  pexpect                                             # Child process spawning and STDOUT redirection

def press(button):
    """
    Handle button events
    """
    
    if( button == "Cancel" ):
        app.stop()                                              # Kill program

    else:
        usr = app.getEntry( "ID\t\t" )                          # Store ID
        cty = app.getOptionBox( "City\t\t" )                    # Store City
        stt = stt_addr[ app.getOptionBox( "Steth.\t" ) ]        # Store Stethoscope

        #dst = "%s%s%s%s" %(snd, usr, cty, fullStamp()[2:4])

        dst = "ABPC_%s_%s_%s_%s.txt" %(usr, cty, stt, fullStamp())    # Create string
        
        print( "Using Stethoscope %s with address %s"
               %(app.getOptionBox( "Steth.\t" ), stt) ) 
        print( "Storing under: %s\n" %dst )
        
        cmd = "python pressureDialGauge_GUI.py --directory %s --destination %s --stethoscope %s" %( cty, dst, stt )

        child = pexpect.spawn(cmd, timeout=None)                # Spawn child

        for line in child:                                      # Read STDOUT ...
            out = line.strip('\n\r')                            # ... of spawned child ...
            print( out )                                        # ... process and print.

        child.close()                                           # Kill child process
        app.destroySubWindow( win_name['2'] )
        app.showSubWindow( win_name['1'] )

# ---------------------------------------------------------------------------------

def launch_win( prompt ):
    
    if( prompt == 'Cancel' ):
        app.stop()                                              # Kill program

    else:
        #
        # Subwindow (1) - Enter SP ID
        #

        #
        # Setup
        #
        app.startSubWindow( win_name['1'], modal=True )         # Start subwindow
        app.setBg( "black" )                                    # Set GLOBAL background color
        app.setFont( size=20 )                                  # Set GLOBAL font size
##        app.setSize( "fullscreen" )                            # Set geometry to fullscreen

        #
        # Add labels
        #
        label_name = "SP_ID_Label"
        app.addLabel( label_name, "Enter SP ID" )               # Create a label
        app.setLabelFg( label_name, "gold" )                    # Set label's font color
        app.setLabelRelief( label_name, "raised" )              # Set relief to raised

        #
        # Add textbox
        #
        app.addLabelEntry( "ID\t\t" )                           # Add an ID entry box
        app.setLabelFg( "ID\t\t", "gold" )                      # Set the color of 'Stethoscope'

        #
        # Add buttons and link them to actions
        #
        app.addButtons( ["Begin"], inst_win )                   # Link buttons to inst_win()

        #
        # Add PD3D logo image
        # 
        app.addImage( win_name['1'], logo )                     # Add PD3D Logo

        #
        # Start subWindow
        #
        app.showSubWindow( win_name['1'] )

# ---------------------------------------------------------------------------------

def inst_win( prompt ):
    
    app.hideSubWindow( win_name['1'] )
    
    if( prompt == 'Begin' ):
        #
        # Subwindow (1) - Enter SP ID
        #

        #
        # Setup
        #
        app.startSubWindow( win_name['2'], modal=True )         # Start subwindow
        app.setBg( "black" )                                    # Set GLOBAL background color
        app.setFont( size=20 )                                  # Set GLOBAL font size
##        app.setSize( "fullscreen" )                             # Set geometry to fullscreen
        
        #
        # Add labels
        #
        app.addLabel( "title_ABPC1", "Instructions" )           # Create a label
        app.setLabelFg( "title_ABPC1", "gold" )                 # Set label's font color
        app.setLabelRelief( "title_ABPC1", "raised" )           # Set relief to raised

        #
        # Add image
        #
        img = "image.gif"
        app.addImage( win_name['2'], img )                      # Add image
        
        #
        # Write down instructions
        #
        app.addMessage("mess", "This is my piece of instructions" )
        app.setMessageBg( "mess", "white" )
        app.setMessageFg( "mess", "black" )
        app.setMessageRelief( "mess", "ridge" )
        app.setMessageWidth( "mess", "600" )
        
        #
        # Link buttons to functions
        #
        app.addButtons( ["Start", "Stop"], press )              # Link buttons to launch_steth()
##        app.addButtons( ["Start", "Stop"], launch_steth )         # Link buttons to launch_steth()


        #
        # Start subWindow
        #
        app.showSubWindow( win_name['2'] )

    else: app.stop()                                            # Kill program

# ---------------------------------------------------------------------------------

def launch_steth( prompt ):
    
    if( prompt == "Start" ):
        usr = app.getEntry( "ID\t\t" )                          # Store ID
        cty = app.getOptionBox( "City\t\t" )                    # Store City
        stt = stt_addr[ app.getOptionBox( "Steth.\t" ) ]        # Store Stethoscope
        app.setMessage("mess", "User: %s\nCity: %s\nSteth: %s" %(usr, cty, stt) )
        print( usr, cty, stt )

    else:
        print( "Gudbay ma fren" )
        app.destroySubWindow( win_name['2'] )
        app.showSubWindow( win_name['1'] )

# ---------------------------------------------------------------------------------

#
# Create a dict with all the stethoscope addresses
#
stt_addr = { 'AS001': "00:06:66:8C:D3:F6",
             'AS002': "00:06:66:8C:9C:2E",
             'AS003': "00:06:66:D0:E4:94" }

#
# Point to logo we desire to use
#
global logo
logo = "pd3d_inverted_with_title.gif"

#
# SubWindow name
#
global win_name
win_name = { '1' : "SP ID"      ,
             '2' : "Intructions",
             '3' : "Nada"         }

#
# Set up
#
app = gui( "Login Window" )                                     # Create a GUI variable
##app.setSize( "fullscreen" )                                     # Launch in fullscreen
app.setBg( "black" )                                            # Set GLOBAL background color
app.setFont( size=20 )                                          # Set GLOBAL font size

#
# add & configure widgets - widgets get a name, to help referencing them later
#
app.addLabel( "main_title", "CSEC" )                            # Create a label
app.setLabelBg( "main_title", "gold" )                          # Set label's background color
app.setLabelFg( "main_title", "black" )                         # Set label's font color

app.setPadding([20,20])                                         # Pad outside the widgets

#
# ...aaaand this is where we add the textboxes
#
app.addLabelOptionBox( "City\t\t",                              # Create a dropdown menu for city
                      ["FL",                                    # ...
                       "TX",                                    # ...
                       "GA",                                    # Populate with cities
                       "PA",                                    # ...
                       "CA"] )                                  # ...
app.setLabelFg( "City\t\t", "gold" )                            # Set the color of 'City'

app.addLabelOptionBox( "Steth.\t",                              # Create a dropdown menu for stethoscopes
                      ["AS001",                                 # ...
                       "AS002",                                 # Populate with stehtoscopes
                       "AS003"] )                               # ...
app.setLabelFg( "Steth.\t", "gold" )                            # Set the color of 'Stethoscope'

#
# Add PD3D logo image
# 
app.addImage( "main_logo", "pd3d_inverted_with_title.gif" )     # Add PD3D Logo


#
# Link buttons to functions
#
app.addButtons( ["Submit", "Cancel"], launch_win )              # Link buttons to launch_win()

#
# Start GUI
#
app.go()
