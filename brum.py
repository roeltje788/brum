#GENERAL
import sys
import argparse

# CUSTOM

# folder:functions
from functions.mode_lookup          import *
from functions.mode_report          import *
from functions.mode_getzone         import *
from functions.mode_batch           import *
from functions.mode_domainreport    import *

class settings:
    def __init__(self,tmp_settings,tmp_arguments = None):

        self.supported      = tmp_settings['supported']
        self.version        = tmp_settings['version']
        self.workers        = tmp_settings['workers']
        self.buffer_reader  = tmp_settings['buffer_reader']
        self.buffer_writer  = tmp_settings['buffer_writer']
        self.sleep_writer   = tmp_settings['sleep_writer']
        self.sleep_reader   = tmp_settings['sleep_reader']

        if (not tmp_arguments == None):

            self.mode           = tmp_arguments.mode
            self.input          = tmp_arguments.input
            self.output         = tmp_arguments.output
            self.reference      = tmp_arguments.reference
            self.country_code   = tmp_arguments.country

def set_settings(argv):

    # Get supported modes
    file_settings   =   {}

    with open('./settings/settings.json') as json_file:

        file_settings       = json.load(json_file)[0]

    tmp_settings = settings(file_settings)

    parser = argparse.ArgumentParser()
    parser.add_argument("mode",choices=tmp_settings.supported,help="The different modes of brum")
    parser.add_argument("-i", "--input" ,help="Input file used by one of the modes")
    parser.add_argument("-o", "--output",help="Output file used by one of the modes")
    parser.add_argument("-r", "--reference",help="Reference file for domain checking")
    parser.add_argument("-c", "--country",help="Country code used in report mode")
    args = parser.parse_args()

    return  settings(file_settings,args)

def welcome_message(new_settings):

    print ("\n")
    print ("Welcome to Brum. A RPKI deployment analysis tool (Version:{})".format(new_settings.version))
    print ("Following functions are supported (-h for help): ", end=' ')

    for p in new_settings.supported:
        print ("{}".format(p),end=' ')
    print ("\n")

def main(argv):

    settings = set_settings(argv) # Get all settings for Brum to run

    welcome_message(settings) # Send the welcome message to the output for the user to read

    #run a supported mode or  give an error

    if (settings.mode == 'lookup'):
        analyse_data(settings)
    elif (settings.mode == 'batchlookup'):
        batch_lookup(settings) #input,workers,lineset
    elif (settings.mode == 'report'):
        generate_report(settings) #input
    elif (settings.mode == 'batchreport'):
        batch_report(settings) #input
    elif (settings.mode == 'getroothints'):
        get_root_hints(settings) #output
    elif (settings.mode == 'getrootzone'):
        get_root_zone(settings) #output
    elif (settings.mode == 'domainreport'):
        generate_domainreport(settings) #input
    else:
        print ('That mode is not (yet) supported.')

#MAIN

if __name__ == "__main__":
   main(sys.argv[1:])
