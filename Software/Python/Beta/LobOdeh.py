'''
*
* LobOdeh Method slope dependant filtering method
*
* VERSION: 0.1
*   - ADDEED  : Initial code.
*
* KNOWN ISSUES:
*   - Needs to be extensively tested and refined
*
* AUTHOR                    :   Mohammad Odeh
* DATE                      :   May.  3rd, 2018 Year of Our Lord
* LAST CONTRIBUTION DATE    :               ---
*
'''

import  numpy                   as      np
import  matplotlib.pyplot       as      plt
import  math


def lobOdeh(xx, yy, ytol_min=0.5, ytol_max=1.0):
    x, y = xx.copy(), yy.copy()

    # Declare required variables
    m = np.zeros_like(x)                                # Slopes array
    b = np.zeros_like(x)                                # Intercept array
    y_prime = np.zeros_like(x)                          # Predicted  y values array

    # Initial values
    m[0] = (y[1]-y[0]) / (x[1]-x[0])                    # Calculate initial slope
    b[0] = y[0]-m[0]*x[0]                               # Calculate initial intercept
    y_prime[0] = y[0]
    
    # Traverse data
    for i in range( 1, len(x) ):
        m[i] = (y[i]-y[i-1]) / (x[i]-x[i-1])            # Calculate slope
        b[i] = y[i-1]-m[i]*x[i]                           # Calculate intercept
        y_prime[i] = m[i-1]*x[i]+b[i-1]                 # Calculate predicted value
        
##        print( "{}:-".format(i) )
##        print( "--------------" )
##        print( "INITIAL VALUES" )
##        print( "--------------" )
##        print( "x[{}]       = {}".format(i, x[i]) )
##        print( "y[{}]       = {}".format(i, y[i]) )
##        print( "y_prime[{}] = {}".format(i, y_prime[i]) )
##        print( "m[{}]       = {}".format(i, m[i]) )
##        print( "b[{}]       = {}".format(i, b[i]) )

        # Check criteria
        if( ytol_min <= y[i] - y_prime[i] and y[i] - y_prime[i] <= ytol_max ):
##        if( m[i] >= 5 ):
##            y[i] = y_prime[i]                           # Attenuate
##            m[i] = (y[i]-y[i-1]) / (x[i]-x[i-1])        # Calculate slope
##            b[i] = y[i-1]-m[i]*x[i]                     # update intercept
##            print( "--------------" )
##            print( "UPDATED VALUES" )
##            print( "--------------" )
##            print( "y_update[{}]= {}".format(i, y[i]) )
##            print( "m[{}]       = {}".format(i, (y[i]-y[i-2]) / (x[i]-x[i-2])) )
##            print( "b[{}]       = {}".format(i, b[i]) )
##
##        print("")
        
    return( x, y )

m, n = list(), list()
fileName = "C:\\Users\\modeh\\Desktop\\output.txt"
i=1
with open(fileName, 'r') as f:
    for line in f:
        line = line.split( ',' )
        i=i+1
        if( 262 <= i and i <= 268):
            m.append( line[0] )
            n.append( line[2].strip('\n') )

x = np.zeros((len(m)), dtype="float64")
y = np.zeros((len(n)), dtype="float64")

for i in range( 0, len(m) ):
    x[i] = m[i]
    y[i] = n[i]

u, v = lobOdeh(x, y, ytol_min=0.001, ytol_max=5.0)
fig, ax = plt.subplots()
original, = ax.plot( x, y, 'b' )
corrected, = ax.plot( u, v, 'r--' )

plt.legend([original, corrected], ["Original", "Corrected"])
plt.grid(True)

##n = np.arange(0,len(x))
##
##for X, Y, N in zip(x, y, n):
##    ax.annotate( '{}: (x={}, y={})'.format(N, X, Y), xy=(X,Y), xytext=(-5, 5), ha='right',
##                textcoords='offset points' )
##
##for U, V, N in zip(u, v, n):
##    ax.annotate( '{}: (x={}, y_predicted={})'.format(N, U, V), xy=(U,V), xytext=(-5, 5), ha='left',
##                textcoords='offset points' )

plt.show()



'''
def genData( length=20 ):
    x = np.zeros((length), dtype="float")
    y = np.zeros_like(x)

    x[0] = 0
    y[0] = 10
    for i in range( 1, len(x) ):
        x[i] = x[0] + i/10.
        y[i] = y[0] - i/10.

    x[length*1/4-1] = x[length*1/4-1] + .25
    x[length*2/4-1] = x[length*2/4-1] + .25
    x[length*3/4-1] = x[length*3/4-1] + .25
    x[length*4/4-1] = x[length*4/4-1] + .25

    return( x, y )

##u, v = genData()
##x, y = lobOdeh(u, v, tol=0.5)
##plot(u,v, x,y, 'r--')
##show()
'''
