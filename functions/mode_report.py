###GENERAL####
import json
import sys
import os
import time
import math
from collections import Counter


##CUSTOM####


#Questions to answer:
'''
    LOOK AT IP-ADDRESSES NOT DOMAIN NAME

    KEEP TIME IN CONSIDERATION, IF PRESENT IT CONTAINS DATA OVER TIME

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

# General

def write_json_file(json_data,location):

    with open(location, "w") as output:
        output.write(json.dumps(json_data, indent=4))

def create_percentage (total,part):

    if (total == 0):
        return 0

    percentage = (round((part/total)*100,2))
    return percentage

# Check if a test can run

def check_argument(input,argument):

    first_line = input[0]

    if (argument in first_line):
        return True
    else:
        return False

def validate_basic_test(input):

    validation_value = 0

    if (check_argument(input,'ns_address')):
        validation_value +=1
    if (check_argument(input,'ip4_address')):
        validation_value +=1
    if (check_argument(input,'ip6_address')):
        validation_value +=1
    if (check_argument(input,'asn')):
        validation_value +=1
    if (check_argument(input,'prefix')):
        validation_value +=1
    if (check_argument(input,'valid_roa')):
        validation_value +=1

    if (validation_value == 6):
        return True
    else:
        return False

def validate_for_tot_argument(json_file):

    return check_argument(json_file,'tot')

def validate_for_country_argument(json_file):

    return check_argument(json_file,'country')

# ALL TESTS

# Basic tests
def valid_roas_in_list(json_file):

    protected = 0

    json_file_max = len(json_file) - 1 # -1 for the upcoming counter

    for i in range(0, json_file_max):
        if (json_file[i]['valid_roa'] == 'valid'):
            protected+=1

    return protected

def valid_ip4_roas_in_list(json_file):

    protected = 0

    json_file_max = len(json_file) - 1 # -1 for the upcoming counter

    for i in range(0, json_file_max):
        if (json_file[i]['valid_roa'] == 'valid' and json_file[i]['ip6_address'] == 'NULL' ):
            protected+=1

    return protected

def valid_ip6_roas_in_list(json_file):

    protected = 0

    json_file_max = len(json_file) - 1 # -1 for the upcoming counter

    for i in range(0, json_file_max):
        if (json_file[i]['valid_roa'] == 'valid' and json_file[i]['ip4_address'] == 'NULL'):
            protected+=1

    return protected



def number_of_errors(json_file):

    errors = 0

    json_file_max = len(json_file) - 1 # -1 for the upcoming counter

    for i in range(0, json_file_max):
        error = False
        if (json_file[i]['prefix'] == 'error'):
            error = True
        if (json_file[i]['asn'] == 'error'):
            error = True
        if (json_file[i]['valid_roa'] == 'error'):
            error = True

        if (error == True):
            errors += 1

    return errors

def number_of_ip4_errors(json_file):

    errors = 0

    json_file_max = len(json_file) - 1 # -1 for the upcoming counter

    for i in range(0, json_file_max):
        error = False
        if (json_file[i]['prefix'] == 'error' and json_file[i]['ip6_address'] == 'NULL'):
            error = True
        if (json_file[i]['asn'] == 'error' and json_file[i]['ip6_address'] == 'NULL'):
            error = True
        if (json_file[i]['valid_roa'] == 'error' and json_file[i]['ip6_address'] == 'NULL'):
            error = True

        if (error == True):
            errors += 1

    return errors

def number_of_ip6_errors(json_file):

    errors = 0

    json_file_max = len(json_file) - 1 # -1 for the upcoming counter

    for i in range(0, json_file_max):
        error = False
        if (json_file[i]['prefix'] == 'error' and json_file[i]['ip4_address'] == 'NULL'):
            error = True
        if (json_file[i]['asn'] == 'error' and json_file[i]['ip4_address'] == 'NULL'):
            error = True
        if (json_file[i]['valid_roa'] == 'error' and json_file[i]['ip4_address'] == 'NULL'):
            error = True

        if (error == True):
            errors += 1

    return errors

def errors_ip_lookup(json_file):

    errors = 0

    json_file_max = len(json_file) - 1 # -1 for the upcoming counter

    for i in range(0, json_file_max):
        error = False
        if (json_file[i]['prefix'] == 'error'):
            error = True
        if (json_file[i]['asn'] == 'error'):
            error = True

        if (error == True):
            errors += 1

    return errors


def errors_roa_lookup(json_file):

    errors = 0

    json_file_max = len(json_file) - 1 # -1 for the upcoming counter

    for i in range(0, json_file_max):
        if (json_file[i]['valid_roa'] == 'error'):
            errors += 1

    return errors


def get_all_errors(json_file):

    errors = {}

    json_file_max = len(json_file) - 1 # -1 for the upcoming counter

    for i in range(0, json_file_max):
        error = False
        if (json_file[i]['prefix'] == 'error'):
            error = True
        if (json_file[i]['asn'] == 'error'):
            error = True
        if (json_file[i]['valid_roa'] == 'error'):
            error = True

        if (error == True):
            error_location = str(i)

            errors[error_location] = json_file[i]

    return errors

def sort_by(json_file,sort_value):

    values = {}

    for single_row in json_file:
        sorter = single_row[sort_value]
        if ( sorter in values):
            values[sorter].append(single_row)
        else:
            new_list = []
            new_list.append(single_row)
            values[sorter] = new_list

    return values

def sort_by_asn(json_file):

    return sort_by(json_file,'asn')

def sort_by_prefix(json_file):

    return sort_by(json_file,'prefix')

def sort_by_roa(json_file):

    return sort_by(json_file,'valid_roa')

def complete_protected_asn_count(asn_ordered):

    protected_asn = 0

    for asn_value in asn_ordered:
        complete_protected = False
        for single_row in asn_ordered[asn_value]:
            if (single_row['valid_roa'] == 'valid'):
                complete_protected = True
        if (complete_protected == True):
            protected_asn+=1

    return protected_asn

def partial_protected_asn_count(asn_ordered):

    partial_protected_asn = 0

    for asn_value in asn_ordered:
        protected   = False
        unprotected = False
        for single_row in asn_ordered[asn_value]:
            if (single_row['valid_roa'] == 'valid'):
                protected = True
            if (single_row['valid_roa'] != 'valid'):
                unprotected = True
        if (protected == True and unprotected == True):
            partial_protected_asn+=1

    return partial_protected_asn


def complete_protected_prefix_count(prefix_ordered):

    protected_prefix = 0

    for prefix_value in prefix_ordered:
        complete_protected = False
        for single_row in prefix_ordered[prefix_value]:
            if (single_row['valid_roa'] == 'valid'):
                complete_protected = True
        if (complete_protected == True):
            protected_prefix+=1

    return protected_prefix

def partial_protected_prefix_count(prefix_ordered):

    partial_protected_prefix = 0

    for prefix_value in prefix_ordered:
        protected   = False
        unprotected = False
        for single_row in prefix_ordered[prefix_value]:
            if (single_row['valid_roa'] == 'valid'):
                protected = True
            if (single_row['valid_roa'] != 'valid'):
                unprotected = True
        if (protected == True and unprotected == True):
            partial_protected_prefix+=1

    return partial_protected_prefix

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

    print ('Test analyses on the first line in the input file. All lines should have the same arguments!')

    #Check test (exit if basic test cannot run)
    if (validate_basic_test(json_file) == True): #Basic test
        print(u'\u2713'+" All basic arguments")

        report_dict['basic']            =   {}
        basic                           =   report_dict['basic']

        basic['row_count']              =   file_length

        basic['roa_validity']           =   {}
        roa_validity                    =   basic['roa_validity']

        roa_validity['valid_roas']      =   valid_roas_in_list(json_file)
        roa_validity['valid_roas_p']    =   create_percentage(file_length,roa_validity['valid_roas'])
        roa_validity['valid_ip4_roas']  =   valid_ip4_roas_in_list(json_file)
        roa_validity['valid_ip4_roas_p']=   create_percentage(roa_validity['valid_roas'],roa_validity['valid_ip4_roas'])
        roa_validity['valid_ip6_roas']  =   valid_ip6_roas_in_list(json_file)
        roa_validity['valid_ip6_roas_p']=   create_percentage(roa_validity['valid_roas'],roa_validity['valid_ip6_roas'])

        asn_ordered                     =   sort_by_asn(json_file)
        prefix_ordered                  =   sort_by_prefix(json_file)
        roa_ordered                     =   sort_by_roa(json_file)

        basic['asn']                    =   {}
        asn                             =   basic['asn']

        asn['unique_asn_count']         =   len(asn_ordered)
        asn['complete_protected_asn']   =   complete_protected_asn_count(asn_ordered)
        asn['complete_protected_asn_p'] =   create_percentage(asn['unique_asn_count'],asn['complete_protected_asn'])
        asn['partial_protected_asn']    =   partial_protected_asn_count(asn_ordered)
        asn['partial_protected_asn_p']  =   create_percentage(asn['unique_asn_count'],asn['partial_protected_asn'])
        asn['unprotected_asn']          =   asn['unique_asn_count'] - asn['complete_protected_asn'] - asn['partial_protected_asn']
        asn['unprotected_asn_p']        =   round(100 - asn['complete_protected_asn_p'] - asn['partial_protected_asn_p'])

        basic['prefix']                 =   {}
        prefix                          =   basic['prefix']

        prefix['unique_prefix_count']   =   len(prefix_ordered)
        prefix['complete_protected_prefix']     =   complete_protected_prefix_count(prefix_ordered)
        prefix['complete_protected_prefix_p']   =   create_percentage(prefix['unique_prefix_count'],prefix['complete_protected_prefix'])
        prefix['partial_protected_prefix']      =   partial_protected_prefix_count(prefix_ordered)
        prefix['partial_protected_prefix_p']    =   create_percentage(prefix['unique_prefix_count'],prefix['partial_protected_prefix'])
        prefix['unprotected_prefix']    =   prefix['unique_prefix_count'] - prefix['complete_protected_prefix'] - prefix['partial_protected_prefix']
        prefix['unprotected_prefix_p']  =   round(100 - prefix['complete_protected_prefix_p'] - prefix['partial_protected_prefix_p'])

        basic['errors']                 =   {}
        errors                          =   basic['errors']

        errors['error_count']           =   number_of_errors(json_file)
        errors['error_count_p']         =   create_percentage(file_length,errors['error_count'])
        errors['error_ip4_count']       =   number_of_ip4_errors(json_file)
        errors['error_ip4_count_p']     =   create_percentage(errors['error_count'],errors['error_ip4_count'])
        errors['error_ip6_count']       =   number_of_ip6_errors(json_file)
        errors['error_ip6_count_p']     =   create_percentage(errors['error_count'],errors['error_ip6_count'])
        errors['error_ip_lookup']       =   errors_ip_lookup(json_file)
        errors['error_ip_lookup_p']     =   create_percentage(errors['error_count'],errors['error_ip_lookup'])
        errors['error_roa_lookup']      =   errors_roa_lookup(json_file)
        errors['error_roa_lookup_p']    =   create_percentage(errors['error_count'],errors['error_roa_lookup'])

    else:
        print (u'\u2717'+' All basic arguments')
        sys.exit(1)

    #Tot argument (validation + tests)

    if (validate_for_tot_argument(json_file) == True):
        print (u'\u2713'+" Tot argument")
        pass # Run tests
    else:
        print (u'\u2717'+" Tot argument")

    #Country argument (validation + tests)

    if (validate_for_country_argument(json_file) == True):
        print (u'\u2713'+" Country argument")
        pass #Run tests
    else:
        print (u'\u2717'+" Country argument")

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

    #Write everything to disk

    write_json_file(report_dict,output) # Write results to disk

    error_file = '{}/reports/{}_{}_report_errors.json'.format(output_directory,file_name,epoch_time)
    error_json = get_all_errors(json_file)
    write_json_file(error_json,error_file) # Write results to disk

    asn_location = '{}/reports/{}_{}_report_asn_ordered.json'.format(output_directory,file_name,epoch_time)
    write_json_file(asn_ordered,asn_location)
    prefix_location = '{}/reports/{}_{}_report_prefix_ordered.json'.format(output_directory,file_name,epoch_time)
    write_json_file(prefix_ordered,prefix_location)
    roa_location = '{}/reports/{}_{}_report_roa_ordered.json'.format(output_directory,file_name,epoch_time)
    write_json_file(roa_ordered,roa_location)



