#GENERAL
import sys

# CUSTOM
from mode_analyse import *
from mode_report import *
from mode_get_root import *
from mode_help import *

def main(argv):

    program_version = ''
    program_supported = ''

    with open('brum.json') as json_file:

        file                = json.load(json_file)[0]
        program_version     = file['version']
        program_supported   = file['supported']

    print ("Welcome to Brum. A RPKI deployment analysis tool")
    print ("Current version of Brum is: {}".format(program_version))
    print ("Currently Brum supports the following functions:\n")
    for p in program_supported:
        print ("\t{}".format(p))
    print ("\n")

    option = ''

    while (option != "exit"):

        option = input("Please type one of the names above or help to get more information about the options:")

        #Set and run mode

        if (option == 'analyse'):
            print ('Mode set to: Analyse')
            analyse_data(argv)
        elif (option == 'createreport'):
            print ('Mode set to: Create Report')
            create_report(argv)
        elif (option == 'readreport'):
            print ('Mode set to: Read Report ')
            read_report(argv)
        elif (option == 'getroot'):
            print ('Mode set to: Get Authorative Root servers')
            get_root(argv)
        elif (option == 'help'):
            print ('Mode set to: Help')
            give_help(argv)
        elif (option == 'exit'):
            print ('Brum will close now')
        else:
            print ('That mode is not (yet) supported. Try Again')

#MAIN

if __name__ == "__main__":
   main(sys.argv[1:])
