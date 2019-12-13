#GENERAL
import sys

# CUSTOM
from mode_lookup import *
from mode_report import *
from mode_getzone import *
from mode_help import *

def main(argv):

    program_version = ''
    program_supported = ''

    with open('brum.json') as json_file:

        file                = json.load(json_file)[0]
        program_version     = file['version']
        program_supported   = file['supported']

    print ("Welcome to Brum. A RPKI deployment analysis tool (Version:{})".format(program_version))
    print ("Following functions are supported: ", end=' ')

    for p in program_supported:
        print ("{}".format(p),end=' ')
    print ("\n")

    option = ''

    try:
        option = sys.argv[1]
    except:
        pass # message is given later

    #Set and run mode

    if (option == 'lookup'):
        analyse_data(argv)
    elif (option == 'createreport'):
        create_report(argv)
    elif (option == 'readreport'):
        read_report(argv)
    elif (option == 'getroothints'):
        get_root_hints(argv)
    elif (option == 'getrootzone'):
        get_root_zone(argv)
    elif (option == 'help'):
        give_help(argv)
    else:
        print ('That mode is not (yet) supported.')

#MAIN

if __name__ == "__main__":
   main(sys.argv[1:])
