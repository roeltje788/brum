#GENERAL
import sys

# CUSTOM
from mode_ziggy import *

def main(argv):

    try:
        #Get mode
        mode = sys.argv[2]

    except e:
        print ('Possible modes are ziggy,ripe or routinator')
        print ('Program exists with exception message:'+ e)
        sys.exit(2)

    #Set and run mode

    if (mode == 'ziggy'):
        print ('Mode set to: Ziggy')
        ask_ziggy(argv)
    if (mode == 'ripe'):
        print ('Mode set to: RIPE')
    if (mode == 'routinator'):
        print ('Mode set to: Routinator')

#MAIN

if __name__ == "__main__":
   main(sys.argv[1:])

'''
first_file = open('first','r')
second_file = open('second','r')

for line in first_file:
    #print (line)
    if line not in second_file.read():
        print ('')
'''
