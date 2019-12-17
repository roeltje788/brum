###GENERAL####
import json
import sys
import os
import time
import math
from collections import Counter
from itertools import islice

#Questions to answer:
'''
    Basic report (arguments:ns_address,ip4_address,ip6_address,asn,prefix):

    Additional argument(s):tot:

    (ignore those without a domain name!!)

    - Give tot number of domains protected (only possible if tot exists)

    Additional argument(s):country:

    -Difference per country?

'''
# General

def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))

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
    def __init__(self,file_length,valid_roas,valid_ip4_roas,valid_ip6_roas,tot,protected_ip4_domains,protected_ip6_domains,country,protected_ip4_netherlands,protected_ip6_netherlands,protected_ip4_netherlands_domains,protected_ip6_netherlands_domains):

        self.json_results                           =   {}

        self.json_results['valid_roas']             =   valid_roas
        self.json_results['valid_roas_p']           =   create_percentage(file_length,valid_roas)
        self.json_results['valid_ip4_roas']         =   valid_ip4_roas
        self.json_results['valid_ip4_roas_p']       =   create_percentage(valid_roas,valid_ip4_roas)
        self.json_results['valid_ip6_roas']         =   valid_ip6_roas
        self.json_results['valid_ip6_roas_p']       =   create_percentage(valid_roas,valid_ip6_roas)
        if (tot):
            self.json_results['protected_domains']      =   protected_ip4_domains + protected_ip6_domains
            self.json_results['protected_ip4_domains']  =   protected_ip4_domains
            self.json_results['protected_ip6_domains']  =   protected_ip6_domains
        if (country):
            self.json_results['protected_netherlands']      =   protected_ip4_netherlands + protected_ip6_netherlands
            self.json_results['protected_ip4_netherlands']  =   protected_ip4_netherlands
            self.json_results['protected_ip6_netherlands']  =   protected_ip6_netherlands
        if (tot and country):
            self.json_results['protected_netherlands_domains']      =   protected_ip4_netherlands_domains + protected_ip6_netherlands_domains
            self.json_results['protected_ip4_netherlands_domains']  =   protected_ip4_netherlands_domains
            self.json_results['protected_ip6_netherlands_domains']  =   protected_ip6_netherlands_domains

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
    def __init__(self,unique_count,complete_protected,partial_protected,file_length,complete_protected_list,partial_protected_list,unprotected_list):

        self.json_results                               =   {}

        self.json_results['unique_count']               =   file_length
        self.json_results['complete_protected']         =   complete_protected
        self.json_results['complete_protected_p']       =   create_percentage(file_length,complete_protected)
        self.json_results['partial_protected']          =   partial_protected
        self.json_results['partial_protected_p']        =   create_percentage(file_length,partial_protected)
        self.json_results['unprotected']                =   file_length - self.json_results['complete_protected'] - self.json_results['partial_protected']
        self.json_results['unprotected_p']              =   round(100 - self.json_results['complete_protected_p'] - self.json_results['partial_protected_p'],2)
        self.json_results['complete_protected_list']    =   complete_protected_list
        self.json_results['partial_protected_list']     =   partial_protected_list
        self.json_results['unprotected_list']           =   unprotected_list

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

# ALL TESTS

# Basic tests
def roa_checker(json_file,tot,country):

    protected_complete                  =   0
    protected_ip4                       =   0
    protected_ip6                       =   0

    protected_ip4_domains               =   0
    protected_ip6_domains               =   0

    protected_ip4_netherlands           =   0
    protected_ip6_netherlands           =   0

    protected_ip4_netherlands_domains   =   0
    protected_ip6_netherlands_domains   =   0


    file_length = len(json_file)

    for single_row in json_file:
        if (single_row['valid_roa'] == 'valid'):
            protected_complete+=1
            if (single_row['ip6_address'] == 'NULL' ):
                protected_ip4+=1
                if(tot):
                    protected_ip4_domains += int(single_row['tot'])
                if(country and single_row['country'] == 'NL'):
                    protected_ip4_netherlands+=1
                    if(tot):
                        protected_ip4_netherlands_domains+= int(single_row['tot'])
            if (single_row['ip4_address'] == 'NULL' ):
                protected_ip6+=1
                if(tot):
                    protected_ip6_domains += int(single_row['tot'])
                if(country and single_row['country'] == 'NL'):
                    protected_ip6_netherlands+=1
                    if(tot):
                        protected_ip6_netherlands_domains+= int(single_row['tot'])


    return roa_analyser(file_length,protected_complete,protected_ip4,protected_ip6,tot,protected_ip4_domains,protected_ip6_domains,country,protected_ip4_netherlands,protected_ip6_netherlands,protected_ip4_netherlands_domains,protected_ip6_netherlands_domains)

def error_checker(json_file):

    errors_complete     =   0
    errors_ip4          =   0
    errors_ip6          =   0
    errors_ip_lookup    =   0
    errors_roa_lookup   =   0
    errors              =   []

    file_length         =   len(json_file)

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

def get_unique_ip(json_file):

    values = {}
    ip_list = []

    for single_row in json_file:
        sorter = ''
        if (single_row['ip4_address'] == 'NULL'):
            sorter = single_row['ip6_address']
        else:
            sorter = single_row['ip4_address']
        if ( sorter in values):
            values[sorter].append(single_row)
        else:
            new_list = []
            new_list.append(single_row)
            values[sorter] = new_list

    for single_row in values:
        ip_list.append(values[single_row][0])

    return ip_list

def ordered_list_checker(ordered_list):

    complete_protected      =       0
    complete_protected_list =       {}
    partial_protected       =       0
    partial_protected_list  =       {}
    unprotected_list        =       {}

    file_length = len(ordered_list)

    for ordered_item in ordered_list:
        single_complete_protected  =   True
        single_partial_protected   =   False
        single_partial_unprotected =   False
        for single_row in ordered_list[ordered_item]:
            if (single_row['valid_roa'] != 'valid'):
                single_complete_protected = False # Complete protection checker
                single_partial_unprotected = True # Partial protection checker
            if (single_row['valid_roa'] == 'valid'):
                single_partial_protected = True # Partial protection checker

        if (single_complete_protected == True):
            complete_protected+=1
            tmp_length                              = len(ordered_list[ordered_item])
            complete_protected_list[str(tmp_length)]   = str(ordered_item)


        elif (single_partial_protected == True and single_partial_unprotected == True):
            partial_protected+=1
            tmp_length                              =   len(ordered_list[ordered_item])
            partial_protected_list[str(tmp_length)] =   str(ordered_item)
        else:
            tmp_length                              =   len(ordered_list[ordered_item])
            unprotected_list[str(tmp_length)]       =   str(ordered_item)

    complete_tmp_list = complete_protected_list.keys()
    complete_tmp_list = list(map(int,complete_tmp_list))
    complete_protected_list = sorted(zip(complete_tmp_list,complete_protected_list.values()),reverse=True)[0:5]

    partial_tmp_list = partial_protected_list.keys()
    partial_tmp_list = list(map(int,partial_tmp_list))
    partial_protected_list = sorted(zip(partial_tmp_list,partial_protected_list.values()),reverse=True)[0:5]

    unprotected_tmp_list    = unprotected_list.keys()
    unprotected_tmp_list    = list(map(int,unprotected_tmp_list))
    unprotected_list        = sorted(zip(unprotected_tmp_list,unprotected_list.values()),reverse=True)[0:5]

    return ordered_list_analyser(file_length,complete_protected,partial_protected,file_length,complete_protected_list,partial_protected_list,unprotected_list)

def basic_tests(json_file,asn_ordered,prefix_ordered,error_results,tot,country):

    json_results                    =   {}

    file_length                     =   len(json_file)

    json_results['row_count']       =   file_length
    json_results['roa_validity']    =   roa_checker(json_file,tot,country).json_object()
    json_results['asn']             =   ordered_list_checker(asn_ordered).json_object()
    json_results['prefix']          =   ordered_list_checker(prefix_ordered).json_object()
    json_results['errors']          =   error_results.json_object()

    return json_results

# Tests for tot argument

def tot_tests(json_file):
    return 0

# Tests for country argument

def country_tests(json_file):
    return 0

# File management

def get_json_file(input):

    input_file = []

    #Open file
    with open(input) as json_input:
        input_file = json.load(json_input)

    return input_file

def write_results_to_disk(input,report_dict,error_results,asn_ordered,prefix_ordered,roa_ordered,ip_ordered):

    # Generate folders and output file names

    base_dir        = os.path.dirname(input)
    file            = os.path.splitext(os.path.basename(input))
    file_name       = file[0]
    file_extension  = file[1]

    epoch_time = int(time.time())

    output_directory = '{}/{}'.format(base_dir,file_name)

    os.system('mkdir -p {}'.format(output_directory))
    os.system('mkdir -p {}/reports/'.format(output_directory))

    os.system('cp {} {}/reports/{}_report_original.json'.format(input,output_directory,file_name)) #Create a copy of $

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
    ip_location = '{}/reports/{}_{}_report_ip_ordered.json'.format(output_directory,file_name,epoch_time)
    write_json_file(ip_ordered,ip_location)

# Main program

def generate_report(input):

    report_dict = {} #This report will contain all results generated below and will later be written to the disk

    json_file = get_json_file(input) #Get the file to make the report for
    file_length = len(json_file)

    print ('Test analyses on the first line in the input file. All lines should have the same arguments!')

    #Check test (exit if basic test cannot run)
    if (validate_basic_test(json_file)): #Basic test
        print(u'\u2713'+" All basic tests")

        # Generate some files ordered differently

        # Sort for domains

        asn_ordered                     =   sort_by(json_file,'asn')
        prefix_ordered                  =   sort_by(json_file,'prefix')
        roa_ordered                     =   sort_by(json_file,'valid_roa')

        # Sort for unique IP's

        unique_ip_list                  =   get_unique_ip(json_file)

        unique_asn_ordered              =   sort_by(unique_ip_list,'asn')
        unique_prefix_ordered           =   sort_by(unique_ip_list,'prefix')
        unique_roa_ordered              =   sort_by(unique_ip_list,'valid_roa')

        # Run basic tests

        tot = False

        if (check_argument(json_file, 'tot')): # TOT
            print (u'\u2713'+" Tot tests")
            tot = True

        country = False

        if (check_argument(json_file, 'country')): # COUNTRY
            print (u'\u2713'+" Country tests")
            country = True


        error_results                   =   error_checker(json_file)
        report_dict['domain']           =   basic_tests(json_file,asn_ordered,prefix_ordered,error_results,tot,country)
        unique_error_results            =   error_checker(unique_ip_list)
        report_dict['ip']               =   basic_tests(json_file,unique_asn_ordered,unique_prefix_ordered,unique_error_results,False,False)
        report_dict['tot']              =   tot_tests(json_file)
        report_dict['country']          =   country_tests(json_file)

    else:
        print (u'\u2717'+' All basic arguments')

    #Generate output files and write to disk

    write_results_to_disk(input,report_dict,error_results,asn_ordered,prefix_ordered,roa_ordered,unique_ip_list)
