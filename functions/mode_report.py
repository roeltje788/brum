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

    Additional argument(s):tot:

    (ignore those without a domain name!!)

    - Give tot number of domains protected (only possible if tot exists)
    - Give top 3 protected and top 3 unprotected domains

    Additional argument(s):country:

    -Difference per country?

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

##CLASSES####

class roa_analyser:
    def __init__(self,valid_roas,valid_ip4_roas,valid_ip6_roas,file_length):

        self.json_results                      =   {}

        self.json_results['valid_roas']        =   valid_roas
        self.json_results['valid_roas_p']      =   create_percentage(file_length,valid_roas)
        self.json_results['valid_ip4_roas']    =   valid_ip4_roas
        self.json_results['valid_ip4_roas_p']  =   create_percentage(valid_roas,valid_ip4_roas)
        self.json_results['valid_ip6_roas']    =   valid_ip6_roas
        self.json_results['valid_ip6_roas_p']  =   create_percentage(valid_roas,valid_ip6_roas)

    def json_object(self):

        return self.json_results

class error_analyser:
    def __init__(self,error_count,error_ip4_count,error_ip6_count,error_ip_lookup,error_roa_lookup,errors,file_length):

        self.json_results                           =   {}

        self.json_results['error_count']            =   error_count
        self.json_results['error_count_p']          =   create_percentage(file_length,error_count)
        self.json_results['error_ip4_count']        =   error_ip4_count
        self.json_results['error_ip4_count_p']      =   create_percentage(error_count,error_ip4_count)
        self.json_results['error_ip6_count']        =   error_ip6_count
        self.json_results['error_ip6_count_p']      =   create_percentage(error_count,error_ip6_count)
        self.json_results['error_ip_lookup']        =   error_ip_lookup
        self.json_results['error_ip_lookup_p']      =   create_percentage(error_count,error_ip_lookup)
        self.json_results['error_roa_lookup']       =   error_roa_lookup
        self.json_results['error_roa_lookup_p']     =   create_percentage(error_count,error_roa_lookup)

        self.errors                                 =   errors

    def json_object(self):

        return self.json_results

    def json_errors(self):

        return self.errors

class ordered_list_analyser:
    def __init__(self,unique_count,complete_protected,partial_protected,file_length):

        self.json_results                               =   {}

        self.json_results['unique_count']               =   file_length
        self.json_results['complete_protected']         =   complete_protected
        self.json_results['complete_protected_p']       =   create_percentage(file_length,complete_protected)
        self.json_results['partial_protected']          =   partial_protected
        self.json_results['partial_protected_p']        =   create_percentage(file_length,partial_protected)
        self.json_results['unprotected']                =   file_length - self.json_results['complete_protected'] - self.json_results['partial_protected']
        self.json_results['unprotected_p']              =   round(100 - self.json_results['complete_protected_p'] - self.json_results['partial_protected_p'],2)

    def json_object(self):

        return self.json_results

# Check if a test can run

def check_argument(input,argument):

    if (argument in input[0]):
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
def roa_checker(json_file,file_length):

    protected_complete  =   0
    protected_ip4       =   0
    protected_ip6       =   0

    for single_row in json_file:
        if (single_row['valid_roa'] == 'valid'):
            protected_complete+=1
            if (single_row['ip6_address'] == 'NULL' ):
                protected_ip4+=1
            if (single_row['ip4_address'] == 'NULL' ):
                protected_ip6+=1

    return roa_analyser(protected_complete,protected_ip4,protected_ip6,file_length)

def error_checker(json_file,file_length):

    errors_complete     =   0
    errors_ip4          =   0
    errors_ip6          =   0
    errors_ip_lookup    =   0
    errors_roa_lookup   =   0
    errors              =   []

    for single_row in json_file:

        error_complete      =   False
        error_ip4           =   False
        error_ip6           =   False
        error_ip_lookup     =   False
        error_roa_lookup    =   False

        if (single_row['prefix'] == 'error'):
            error_complete = True
            error_ip_lookup = True
            if (single_row['ip6_address'] == 'NULL'):
                error_ip4 = True
            if (single_row['ip4_address'] == 'NULL'):
                error_ip6 = True
        if (single_row['asn'] == 'error'):
            error_complete = True
            error_ip_lookup = True
            if (single_row['ip6_address'] == 'NULL'):
                error_ip4 = True
            if (single_row['ip4_address'] == 'NULL'):
                error_ip6 = True
        if (single_row['valid_roa'] == 'error'):
            error_complete = True
            error_roa_lookup = True
            if (single_row['ip6_address'] == 'NULL'):
                error_ip4 = True
            if (single_row['ip4_address'] == 'NULL'):
                error_ip6 = True

        if (error_complete == True):
            errors_complete += 1
            errors.append(single_row)
        if (error_ip4 == True):
            errors_ip4 += 1
        if (error_ip6 == True):
            errors_ip6 += 1
        if (error_ip_lookup):
            errors_ip_lookup +=1
        if (error_roa_lookup):
            errors_roa_lookup +=1

    return error_analyser(errors_complete,errors_ip4,errors_ip6,errors_ip_lookup,errors_roa_lookup,errors,file_length)

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

def ordered_list_analysis(ordered_list):

    complete_protected      =   0
    partial_protected       =   0

    file_length = len(ordered_list)

    for ordered_item in ordered_list:
        single_complete_protected  =   True
        single_partial_protected   =   False
        single_partial_unprotected =   False
        for single_row in ordered_list[ordered_item]:
            # Complete protection checker
            if (single_row['valid_roa'] != 'valid'):
                single_complete_protected = False # Complete protection checker
                single_partial_unprotected = True # Partial protection checker
            if (single_row['valid_roa'] == 'valid'):
                single_partial_protected = True # Partial protection checker

        if (single_complete_protected == True):
            complete_protected+=1

        if (single_partial_protected == True and single_partial_unprotected == True):
            partial_protected+=1

    return ordered_list_analyser(file_length,complete_protected,partial_protected,file_length)

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

        # Generate some files ordered differently

        asn_ordered                     =   sort_by_asn(json_file)
        prefix_ordered                  =   sort_by_prefix(json_file)
        roa_ordered                     =   sort_by_roa(json_file)

        # Fill object with results

        report_dict['basic']            =   {}
        basic                           =   report_dict['basic']

        basic['row_count']              =   file_length
        basic['roa_validity']           =   roa_checker(json_file,file_length).json_object()
        basic['asn']                    =   ordered_list_analysis(asn_ordered).json_object()
        basic['prefix']                 =   ordered_list_analysis(prefix_ordered).json_object()
        error_results                   =   error_checker(json_file,file_length)
        basic['errors']                 =   error_results.json_object()

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
    error_json = error_results.json_errors()
    write_json_file(error_json,error_file) # Write results to disk

    asn_location = '{}/reports/{}_{}_report_asn_ordered.json'.format(output_directory,file_name,epoch_time)
    write_json_file(asn_ordered,asn_location)
    prefix_location = '{}/reports/{}_{}_report_prefix_ordered.json'.format(output_directory,file_name,epoch_time)
    write_json_file(prefix_ordered,prefix_location)
    roa_location = '{}/reports/{}_{}_report_roa_ordered.json'.format(output_directory,file_name,epoch_time)
    write_json_file(roa_ordered,roa_location)



