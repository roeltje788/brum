#GENERAL
import os
import sys
import getopt
import json
from netaddr import IPNetwork,IPAddress

# CUSTOM
from networking import *
from ziggy_updater import *
from check_file import *

def ask_ziggy(argv):

    #UPDATE ZIGGY
    #LINK: https://www.tutorialspoint.com/python/python_command_line_arguments.htm

    try:
        opts, args = getopt.getopt(argv,"m:d:i:",["mode=","date=","input="])
    except getopt.GetoptError:
        print ('use arguments -m -d and -i')
        sys.exit(2)
    except:
        print ('Some argument is incorrectly set, review the usage of this program in the documentation')


    input = ''

    #Loop through arguments
    for opt, arg in opts:

        if opt in ("-d", "--date"): #Set date
           date = arg
           check_ziggy_with_date(date)
        if opt in ("-i", "--input"): #Set input file
            input = arg


    date = open('.date.txt','r')
    ziggy_date = date.read().splitlines()[1]
    date.close()

    check_file_with_date_and_file(ziggy_date,input)
