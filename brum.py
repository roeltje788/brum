#GENERAL
import sys
import argparse

# CUSTOM

# folder:functions
from functions.mode_lookup  import *
from functions.mode_report  import *
from functions.mode_getzone import *
from functions.mode_batch   import *

def get_arguments(argv):

    # Get supported modes
    supported_list      = []
    program_version     = ''
    program_supported   = ''
    workers             = ''

    with open('./settings/settings.json') as json_file:

        file                = json.load(json_file)[0]
        program_supported   = file['supported']
        program_version     = file['version']
        workers             = file['workers']

    for p in program_supported:
        supported_list.append(p)

    parser = argparse.ArgumentParser()
    parser.add_argument("mode",choices=supported_list,help="The different modes of brum")
    parser.add_argument("-i", "--input" ,help="Input file used by one of the modes")
    parser.add_argument("-o", "--output",help="Output file used by one of the modes")
    args = parser.parse_args()

    total_args = [args,supported_list,program_version,workers]

    return total_args

def main(argv):

    total_arguments = get_arguments(argv)

    arguments       = total_arguments[0]
    supported_list  = total_arguments[1]
    program_version = total_arguments[2]
    workers         = total_arguments[3]

    print ("\n")
    print ("Welcome to Brum. A RPKI deployment analysis tool (Version:{})".format(program_version))
    print ("Following functions are supported (-h for help): ", end=' ')

    for p in supported_list:
        print ("{}".format(p),end=' ')
    print ("\n")

    option = arguments.mode

    #Set and run mode

    if (option == 'lookup'):
        analyse_data(arguments.input,workers)
    elif (option == 'report'):
        generate_report(arguments.input)
    elif (option == 'getroothints'):
        get_root_hints(arguments.output)
    elif (option == 'getrootzone'):
        get_root_zone(arguments.output)
    elif (option == 'batchreport'):
        batch_report(arguments.input)
    elif (option == 'batchlookup'):
        batch_lookup(arguments.input,workers)
    else:
        print ('That mode is not (yet) supported.')

#MAIN

if __name__ == "__main__":
   main(sys.argv[1:])
