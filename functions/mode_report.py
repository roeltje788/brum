###GENERAL####
import json
import sys
import os
import time

##CUSTOM####


#Questions to answer:
'''
    LOOK AT IP-ADDRESSES NOT DOMAIN NAME

    Basic report (arguments:ns_address,ip4_address,ip6_address,asn,prefix):

    - Give overall valid roa
    - Give overall valid roa ipv4 vs ipv6

    Additional argument(s):tot:

    (ignore those without a domain name!!)

    - Give tot number of domains protected (only possible if tot exists)
    - Give top 3 protected and top 3 unprotected domains

    Additional argument(s):country:

    -Difference per country?

    OUTPUT:
    - Generate file with all errors
    - Generate an original file
    - Generate folder for all output
    - Generate file with the above result in .json
    - Generate file from the .json file with the results in human readable version
'''

# Check if a test can run

def validate_basic_test(input):

    validation_value = 0

    first_line = input[0]

    if ('ns_address' in first_line):
        validation_value +=1
    if ('ip4_address' in first_line):
        validation_value +=1
    if ('ip6_address' in first_line):
        validation_value +=1
    if ('asn' in first_line):
        validation_value +=1
    if ('prefix' in first_line):
        validation_value +=1
    if ('valid_roa' in first_line):
        validation_value +=1

    print ('{}'.format(validation_value))

    if (validation_value == 6):
        return True
    else:
        return False

def validate_for_tot_argument(json_file):

    first_line = json_file[0]

    if ('tot' in first_line):
        return True
    else:
        return False

def validate_for_country_argument():

    first_line = json_file[0]

    if ('country' in first_line):
        return True
    else:
        return False


# ALL TESTS

# Basic tests
def valid_roas_in_list(json_file):

    protected = 0

    json_file_max = len(json_file) - 1 # -1 for the upcoming counter
    print ('file length:{}'.format(json_file_max))


    for i in range(0, json_file_max):
        if (json_file[i]['valid_roa'] == 'valid'):
            protected+=1

    return protected

def number_of_errors(json_file):
    pass

# Tests for tot argument


# Tests for country argument


# File management

def get_json_file(input):

    input_file = []

    #Open file
    with open(input) as json_input:
        input_file = json.load(json_input)

    return input_file

# Main program

def generate_report(input):

    report_dict = {} #This report will contain all results generated below and will later be written to the disk

    json_file = get_json_file(input) #Get the file to make the report for
    file_length = len(json_file)
    report_dict['file_length'] = file_length

    print ('Brum will analyse the first line to know how many analysis it can run. Make sure every line has the SAME amount of arguments. Otherwise Brum WILL fail!')

    #Check test (exit if basic test cannot run)
    if (validate_basic_test(json_file) == True): #Basic test
        print("All arguments for the basic test exist. Brum will run those tests now")
        print ('{}'.format(valid_roas_in_list(json_file)))
        report_dict['valid_roas']   =   valid_roas_in_list(json_file)
        #report_dict['error_count']  =   number_of_errors(json_file)
    else:
        print ('Not enough arguments exist to run the basic test. Brum will exit now.')
        sys.exit(1)

    #Tot argument (validation + tests)

    if (validate_for_tot_argument(json_file) == True):
        print ("tot argument in input file, will run the tests for this argument now")
        pass # Run tests
    else:
        print ("tot argument not in input file, skipping those tests.")

    #Country argument (validation + tests)

    if (validate_for_tot_argument(json_file) == True):
        print ("country argument in input file, will run the tests for this argument now")
        pass #Run tests
    else:
        print ("country argument not in input file, skipping those tests.")

    #Generate output files and write to disk

    base_dir        = os.path.dirname(input)
    file            = os.path.splitext(os.path.basename(input))
    file_name       = file[0]
    file_extension  = file[1]

    output_directory = '{}/{}'.format(base_dir,file_name)

    os.system('mkdir -p {}'.format(output_directory))
    os.system('mkdir -p {}/reports/'.format(output_directory))

    os.system('cp {} {}/reports/{}_report_original.json'.format(input,output_directory,file_name)) #Create a copy of the original file

    epoch_time = int(time.time())

    output = '{}/reports/{}_{}_report_results.json'.format(output_directory,file_name,epoch_time)
    os.system('cp {} {}'.format(input,output))

    with open(output, "w") as output:
        output.write(json.dumps(report_dict))



