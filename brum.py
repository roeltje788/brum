#GENERAL
import sys
import argparse

# CUSTOM
from functions.mode_lookup import *
from functions.mode_createreport import *
from functions.mode_readreport import *
from functions.mode_getzone import *
from functions.mode_help import *

def get_arguments(argv):

    # Get supported modes
    supported_list      = []
    program_version     = ''
    program_supported   = ''

    with open('./settings/brum.json') as json_file:

        file                = json.load(json_file)[0]
        program_supported   = file['supported']
        program_version     = file['version']

    for p in program_supported:
        supported_list.append(p)

    parser = argparse.ArgumentParser()
    parser.add_argument("mode",choices=supported_list,help="Output file for this function")
    parser.add_argument("-i", "--input" ,help="Input file for this function")
    parser.add_argument("-o", "--output",help="Output file for this function")
    args = parser.parse_args()

    total_args = [args,supported_list,program_version]

    return total_args

def main(argv):

    total_arguments = get_arguments(argv)

    arguments       = total_arguments[0]
    supported_list  = total_arguments[1]
    program_version = total_arguments[2]

    print ("Welcome to Brum. A RPKI deployment analysis tool (Version:{})".format(program_version))
    print ("Following functions are supported: ", end=' ')

    for p in supported_list:
        print ("{}".format(p),end=' ')
    print ("\n")

    option = arguments.mode

    #Set and run mode

    if (option == 'lookup'):
        analyse_data(argv)
    elif (option == 'createreport'):
        create_report(argv)
    elif (option == 'readreport'):
        read_report(argv)
    elif (option == 'getroothints'):
        get_root_hints(arguments.output)
    elif (option == 'getrootzone'):
        get_root_zone(arguments.output)
    elif (option == 'help'):
        give_help(argv)
    else:
        print ('That mode is not (yet) supported.')

#MAIN

if __name__ == "__main__":
   main(sys.argv[1:])
