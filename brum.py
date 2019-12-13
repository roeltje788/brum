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
    print ("Interactive mode active, since no arguments are given")
    print ("Following functions are supported:\n")
    #print (u'\u2713')
    for p in program_supported:
        print ("\t{}".format(p))
    print ("\n")

    option = ''

    while (option != "exit"):

        option = input("Please type one of the names above or help for more info:")

        #Set and run mode

        if (option == 'lookup'):
            print ('Mode set to: Lookup')
            analyse_data(argv)
        elif (option == 'createreport'):
            print ('Mode set to: Create Report')
            create_report(argv)
        elif (option == 'readreport'):
            print ('Mode set to: Read Report ')
            read_report(argv)
        elif (option == 'getroothints'):
            print ('Mode set to: Get Authorative Hint Root servers')
            get_root_hints(argv)
        elif (option == 'getrootzone'):
            print ('Mode set to: Get entire Authorative Root server zone')
            get_root_zone(argv)
        elif (option == 'help'):
            print ('Mode set to: Help')
            give_help(argv)
        elif (option == 'exit'):
           print ('Closing Brum')
        else:
            print ('That mode is not (yet) supported. Try Again')

#MAIN

if __name__ == "__main__":
   main(sys.argv[1:])
