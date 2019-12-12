#GENERAL
import sys

# CUSTOM
from mode_ripe import *

def main(argv):

    try:
        #Get mode
        mode = sys.argv[2]

    except e:
        print ('Possible modes are ripe')
        print ('Program exits with exception message:'+ e)
        sys.exit(2)

    #Set and run mode

    if (mode == 'ripe'):
        print ('Mode set to: RIPE')
        ask_ripe(argv)

#MAIN

if __name__ == "__main__":
   main(sys.argv[1:])
