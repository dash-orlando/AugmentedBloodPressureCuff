'''
*
* GUI using appJar for Augmented Blood Pressure Cuff
*
* VERSION: 0.1.1
*   - ADDED   : Initial version
*   - ADDED   : Select stethoscope prior to launching dial
*
* KNOWN ISSUES:
*   - None atm
*
* AUTHOR                    :   Mohammad Odeh
* DATE                      :   Nov. 15th, 2017 Year of Our Lord
* LAST CONTRIBUTION DATE    :   Nov. 21st, 2017 Year of Our Lord
*
'''

# Import the library
from    appJar                  import gui                  # Import GUI
from    timeStamp               import fullStamp            # Show date/time on console output
import  pressureDialGauge_GUI                               # Import pressureDialGauge

def press(button):
    """
    Handle button events
    """
    
    if( button == "Cancel" ):
        app.stop()                                          # Kill program

    else:
        usr = app.getEntry( "ID\t\t" )                      # Store ID
        cty = app.getOptionBox( "City\t\t" )                # Store City
        stt = stt_addr[ app.getOptionBox( "Steth.\t" ) ]    # Store Stethoscope

        dst = "/ABPC_%s_%s_%s.txt" %(usr, cty, fullStamp()) # Create string
        
        print( "Using Stethoscope %s with address %s"
               %(app.getOptionBox( "Steth.\t" ), stt) ) 
        print( "Storing under: %s\n" %dst )
        
        pressureDialGauge_GUI.main( cty, dst, stt )         # Start dial gauge!

#
# Create a dict with all the stethoscope addresses
#

stt_addr = { 'AS001': "00:06:66:D0:E4:37",
             'AS002': "00:06:66:8C:9C:2E",
             'AS003': "00:06:66:D0:E4:94" }
#
# Set up
#
app = gui( "Login Window", "600x600" )                      # Create a GUI variable (Length x Height)
app.setBg( "black" )                                        # Set GLOBAL background color
app.setFont( 20 )                                           # Set GLOBAL font size

#
# add & configure widgets - widgets get a name, to help referencing them later
#
app.addLabel( "title", "CSEC" )                             # Create a label
app.setLabelBg( "title", "gold" )                           # Set label's background color
app.setLabelFg( "title", "black" )                          # Set label's font color

app.setPadding([20,20])                                     # Pad outside the widgets

app.addLabelEntry( "ID\t\t" )                               # Add an ID entry box
app.setLabelFg( "ID\t\t", "gold" )                          # Set the color of 'ID'
app.setFocus( "ID\t\t" )                                    # Start the GUI with cursor in 'ID' box

app.addLabelOptionBox( "City\t\t",                          # Create a dropdown menu for city
                      ["Orlando",
                       "Houston",
                       "Racoon City",
                       "Gotham"] )
app.setLabelFg( "City\t\t", "gold" )                        # Set the color of 'City'

app.addLabelOptionBox( "Steth.\t",                          # Create a dropdown menu for stethoscopes
                      ["AS001",
                       "AS002",
                       "AS003"] )
app.setLabelFg( "Steth.\t", "gold" )                        # Set the color of 'Stethoscope'

app.addImage( "logo", "pd3d_inverted_with_title.gif" )      # Add PD3D Logo

#
# Link buttons to functions
#
app.addButtons( ["Submit", "Cancel"], press )               # Link buttons to press()

#
# Start GUI
#
app.go()
