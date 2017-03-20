'''
#
# A program that displays pressure in kPa on a TFT screen.
# ADC converter is used to supplement the RPi given that it has no analop pins
#
# Author: Mohammad Odeh
# Date: Mar. 2nd, 2017
#
'''

# Import modules and libraries
import  time
import  Adafruit_ADS1x15    # Required library for ADC converter
from    numpy import interp # Required for mapping values

# Define the value of the supply voltage of the pressure sensor
V_supply = 3.3

# Initialize ADC
ADC = Adafruit_ADS1x15.ADS1115()
GAIN = 1 # Reads values in the range of +/-4.096V

while True:
    # Read the voltage output of the pressure sensor and map it
    V_analogRead = ADC.read_adc(0, gain=GAIN)
    V_out = interp(V_analogRead, [1235,19279.4116], [0.16,2.41])
    pressure = (V_out/V_supply - 0.04)/0.018
    print("Pressure: %.2fkPa ||  %.2fmmHg" %(pressure, pressure*760/101.3))
    print("AnalogRead: %i  || V_out: %.2f" %(V_analogRead, V_out))
    print("-------------------------------")
    time.sleep(1)
