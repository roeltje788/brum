# GENERAL IMPORTS
import csv
import json
import time
import concurrent.futures
import queue
import threading
import os
import sys
import getopt
import math

# CUSTOM IMPORTS

# FUNCTIONS

def is_ip_ipv6(input):

    if (input['ip6_address'] == 'NULL' or input['ip6_address'] == ''):
        return False
    else:
        return True

class thread_obj():

    def __init__(self):
        self.running = True

    def stop(self):
        self.running = False

class reader_obj(thread_obj):

    def run(self,input,reader_queue,buffer_size,sleep_reader):

        first_line = True
        header = []

        with open(input) as csv_input:
            for line in csv_input:
                line = line.splitlines()
                list_line = line[0].split(',')
                if(first_line):
                    header = list_line
                    first_line = False
                else:
                    dict_line = dict(zip(header,list_line))
                    while (reader_queue.qsize()>=buffer_size): # Wait for the buffer to drop below a threshold
                        time.sleep(sleep_reader)
                    #Buffer is small enough add an item
                    reader_queue.put(dict_line)

def update_result(tmp_result,input_line):

    tmp_result['total']+=1

    is_ipv6 = is_ip_ipv6(input_line) # Is it ipv6?

    if (is_ipv6):
        tmp_result['ipv6_total']+=1
    else:
        tmp_result['ipv4_total']+=1

    if (input_line['valid_roa'] == 'valid'):

        tmp_result['total_protected']+=1

        if (is_ipv6):
            tmp_result['ipv6_protected']+=1
        else:
            tmp_result['ipv4_protected']+=1

    return tmp_result

def get_base_result(tmp_TLD,type):

    tmp_single_TLD_report = {
        'TLD': tmp_TLD ,
        'type': type,
        'total':0,
        'total_protected':0,
        'ipv4_total':0,
        'ipv4_protected':0,
        'ipv6_total':0,
        'ipv6_protected':0
    }

    if (tmp_TLD == 'cpa'):
        print(tmp_single_TLD_report)

    return  tmp_single_TLD_report

class analyser_obj(thread_obj):

    def run(self,reader_queue,writer_queue,reference):

        result              =   {} # This input has been checked with the reference
        result['errors']    =   0 # Initialize the error count

        # Look through input

        while (self.running or not reader_queue.empty()):

            input_line = []

            if (not reader_queue.empty()):
                input_line  = reader_queue.get() #Get line

            else:
                continue

            ns_address          =   input_line['ns_address']
            split_ns_address    =   ns_address.split('.')

            tmp_TLD             =   split_ns_address[-2]

            valid_roa           =   input_line['valid_roa']


            # Does this TLD already exist?

            tmp_result          =   {}

            if (tmp_TLD in result):

                tmp_result = result[tmp_TLD]

            else:

                # This TLD does not exist, create a new instance
                with open(reference) as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:

                        if (row['Domain'] == tmp_TLD):

                            tmp_result = get_base_result(tmp_TLD,row['Type'])
                            continue

            if (len(tmp_result) != 0): # Does this TLD exist in the reference?
                result[tmp_TLD] = update_result(tmp_result,input_line)
            else:
                result['errors']+=1

        writer_queue.put(result)

def get_basic_deep_result():

    tmp         =   {
        'total':0,
        'total_protected':0,
        'ipv4_total':0,
        'ipv4_protected':0,
        'ipv6_total':0,
        'ipv6_protected':0
    }

    return tmp

def deep_analyser(final_results,errors):

    # Initialize results for deep analyser

    deep_results                        =   {}
    deep_results['generic']             =   get_basic_deep_result()
    deep_results['country-code']        =   get_basic_deep_result()
    deep_results['sponsored']           =   get_basic_deep_result()
    deep_results['infrastructure']      =   get_basic_deep_result()
    deep_results['generic-restricted']  =   get_basic_deep_result()

    deep_results['errors']              =   errors

    # Generate deep results

    for row in final_results:

        deep_results[row['type']]['total']              +=  row['total']
        deep_results[row['type']]['total_protected']    +=  row['total_protected']
        deep_results[row['type']]['ipv4_total']         +=  row['ipv4_total']
        deep_results[row['type']]['ipv4_protected']     +=  row['ipv4_protected']
        deep_results[row['type']]['ipv6_total']         +=  row['ipv6_total']
        deep_results[row['type']]['ipv6_protected']     +=  row['ipv6_protected']

    return deep_results

def writer_func(writer_queue,output):

    results         =   writer_queue.get()

    final_results   =   list(results.values()) # Only get a list of all the values to write to the disk

    errors          =   final_results[0]    # Get the errors during report creation
    final_results.pop(0)                    # Remove errors from list

    header          =   final_results[0].keys()

    # Write results for all TLD's

    with open(output,'a') as output_file:
        csv_writer = csv.DictWriter(output_file, fieldnames=header)
        csv_writer.writeheader() # write header
        csv_writer.writerows(final_results)

    # Write deep results

    deep_results = deep_analyser(final_results,errors)

    base_dir        =   os.path.dirname(output)
    file            =   os.path.splitext(os.path.basename(output))
    file_name       =   file[0]
    file_extension  =   file[1]

    deep_output     =   '{}{}{}'.format(base_dir,file_name,'_deep.json')

    with open(deep_output, "w") as output:
        output.write(json.dumps(deep_results, indent=4))

def init_disk(input,epoch_time):

    #Split input
    base_dir        = os.path.dirname(input)
    file            = os.path.splitext(os.path.basename(input))
    file_name       = file[0]
    file_extension  = file[1]

    output_directory = '{}/{}_rootreports'.format(base_dir,file_name)

    os.system('mkdir -p {}'.format(output_directory))

    output = '{}/{}_{}_rootreport.csv'.format(output_directory,file_name,epoch_time)
    os.system('touch {}'.format(output))

    return output

def get_filesize(input):

    filesize = 0

    with open(input) as tmp:
        filesize = sum(1 for line in tmp)

    filesize = filesize - 1 #correcting for first line, this line gives the names of the columns

    return filesize

    print ('The file contains {} lines'.format(filesize))

def thread_handler(reader,tmp_analyser,analyser):

    # Reader

    reader.join()   # Wait until the last line is read

    # Analyser

    tmp_analyser.stop() # Signal to the analyser that the last line has been read into memory
    analyser.join() # Wait for the analyser to finish analysing

def generate_rootreport(settings):

    # Initialize

    start = time.time() #Start keeping track of the time

    output = init_disk(settings.input,start) # Generate a new file to write the results to

    filesize = get_filesize(settings.input) # Lookup the filesize of this file

    print ('This file contains :{} lines'.format(filesize))

    reader_queue        = queue.Queue() # Items that have been read from the file that needs to be checked
    writer_queue        = queue.Queue() # Items in this list have been checked and will be written to the disk

    # Generate report

    # This thread will read the root zone and put them one by one in the queue
    # This way the memory usage is kept low
    reader = threading.Thread(target=reader_obj().run,args=(settings.input,reader_queue,settings.buffer_reader,settings.sleep_reader))
    reader.start()
    # This thread will analyse the data put them in a new queue
    tmp_analyser = analyser_obj()
    analyser = threading.Thread(target=tmp_analyser.run,args=(reader_queue,writer_queue,settings.reference))
    analyser.start()

    # Wait for the report to finish
    thread_handler(reader,tmp_analyser,analyser)

    # Write the results to the disk
    writer_func(writer_queue,output)

    # Finilize

    end = time.time() #End keeping track of time

    time_difference = math.ceil(end - start)
    print("Report generation is done, it took: {} seconds".format(time_difference)) #Give back the result

