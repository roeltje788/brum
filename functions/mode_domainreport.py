# GENERAL IMPORTS
import csv
import json
import os
import math

# Classes

class result_obj:
    def __init__(self,domain_name):

        self.protected = 0
        self.unprotected = 0
        self.error = 0
        self.domain_name = domain_name

# Helper functions

def progress(ticker,progression,percent=0, width=40):
    left = width * percent // 100
    right = width - left
    print('\r{}['.format(ticker), '#' * left, ' ' * right, ']',
          f' {percent:.0f}%',' ','{}'.format(progression),
          sep='', end='', flush=True)

def update_ticker(ticker):

    if (ticker == '|'):
        return '-'
    else:
        return '|'

def write_results_to_disk(result_dict,input):

    base_dir        = os.path.dirname(input)
    file            = os.path.splitext(os.path.basename(input))
    file_name       = file[0]
    file_extension  = file[1]

    output = base_dir+'/'+file_name+'_results.json'

    print('output:{}'.format(output))
    print('input:{}'.format(input))

    os.system('touch {}'.format(output)) # Create file

    #Write to the output file
    with open(output,'w') as new_file:
        json.dump(result_dict,new_file,indent=4)

# Start function

def generate_report(settings):

    # Get input files

    input = settings.input
    reference = settings.reference

    # Open files

    ref_dict    =   {}
    result_dict =   {}

    #CSV to json
    os.system('csvtojson {} > {}.json'.format(reference,reference))

    #Open file
    with open(reference+'.json') as tmp_file:
       ref_dict = json.load(tmp_file)

    # Get filesize

    with open(settings.input) as tmp:
        filesize = sum(1 for line in tmp)

    filesize = filesize - 1 #correcting for first line, this line gives the names of the columns

    print ('The file contains {} lines'.format(filesize))

    # Cross reference

    first_line = True
    header = []

    progression = 0

    ticker = '-'

    with open(input) as input_dict:
        for line in input_dict:

            # Update info for user

            ticker = update_ticker(ticker)
            progression +=1
            progression_percentage = math.floor((progression/filesize)*100)
            progress(ticker,progression,progression_percentage)

            # Calculate cross reference

            line = line.splitlines()
            list_line = line[0].split(',')

            if(first_line):
                header = list_line
                first_line = False
            else:

                dict_line = dict(zip(header,list_line))

                response_name = dict_line['response_name']

                if response_name not in result_dict:
                    result_dict[response_name] = result_obj(response_name)

                for cross in ref_dict:
                    if (dict_line['ns_address'] == cross['ns_address']):
                        if( cross['valid_roa'] == 'valid' ):
                            result_dict[response_name].protected   += 1
                        else:
                            result_dict[response_name].unprotected += 1

                        continue # We are done exit for loop

    progress(u'\u2713',100) # Generating is done

    # Generate results

    protected           =   0
    partial_protected   =   0
    unprotected         =   0
    error               =   0

    for domain in result_dict:
        print('{}'.format(domain))
        if (result_dict[domain].protected == 0 and result_dict[domain].unprotected == 0): # Strange behaviour -> error
            error+=1
        elif (result_dict[domain].protected == 0):   # Complete unprotected
            unprotected+=1
        elif (result_dict[domain].unprotected == 0): # Complete protected
            protected+=1
        else:                           # Partially protected
            partial_protected+=1

    # Add results to dictionary

    results = {}
    results['protected']            =   protected
    results['partial_protected']    =   partial_protected
    results['unprotected']          =   unprotected
    results['error']                =   error

    # Write results to the disk

    write_results_to_disk(results,input)
