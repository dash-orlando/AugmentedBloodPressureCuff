import paho.mqtt.client as mqtt

# This is the Subscriber
def on_connect( client, userdata, flags, rc ):
    print( "Connected with result code " + str(rc) )
##    client.subscribe("pd3d/test/Moe")
    client.subscribe("pd3d/test/sample")

def on_message( client, userdata, msg ):
    if( msg.payload == 'Q' ):
      client.disconnect()

    else:
      print( msg.payload )

IP_addr = "10.190.11.172"
##IP_addr = "192.168.42.1"
port = 1883
client = mqtt.Client()
client.connect( IP_addr, port, 60 )

client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()
