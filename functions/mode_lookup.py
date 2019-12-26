###GENERAL####
import os
import sys
import getopt
import requests
import json
import time
import concurrent.futures
import queue
import threading
import math
import time
import csv

class lookup_obj:
    def __init__(self,line_obj,linenumber):
        self.line_obj = line_obj
        self.linenumber = linenumber

def split(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out

def lookupip(ip):

    json_response = ''

    correct_response = False

    # Connect to server and get a response (keep trying until a good response)

    while (correct_response == False):
        try:
            url = 'https://stat.ripe.net/data/network-info/data.json?resource='+ip
            r = requests.get(url, timeout = 5)
            json_response = json.loads(r.content)
            correct_response = True
        except:
            pass # Try again

    # Use response and put in a usable format

    try:
        prefix  =   json_response['data']['prefix']
        asn     =   json_response['data']['asns'][0]

        if (len(prefix) == 0):
            prefix = 'error'
        if (len(asn) == 0):
            asn = 'error'

        result = [prefix,asn]
        return result
    except:
        return ['error','error']

def check_roa(prefix,asn):

    # Make request (keep trying until a good response)

    json_response = ''
    correct_response = False

    while (correct_response == False):

        try:
            url = 'https://stat.ripe.net/data/rpki-validation/data.json?resource='+asn+'&prefix='+prefix
            r = requests.get(url, timeout = 5)
            json_response = json.loads(r.content)
            correct_response = True
        except:
            pass # Try again

    # Use response and return data
    try:
        return json_response['data']['status']
    except:
        return 'error'

def checkip(checked_list,sub_list_part,dns_servers):

    protected = 0

    for i in sub_list_part:

        ip = ''

        if (dns_servers[i]['ip6_address'] == 'NULL'):
            ip = dns_servers[i]['ip4_address']
        else:
            ip = dns_servers[i]['ip6_address']

        tmp_result  = lookupip(ip)

        dns_servers[i]['prefix']  = tmp_result[0]
        dns_servers[i]['asn']     = tmp_result[1]

        dns_servers[i]['valid_roa']  = check_roa(tmp_result[0],tmp_result[1])

        final_result = [i,dns_servers[i]]

        checked_list.put(final_result)

def create_workers(checked_list,sub_list_parts,dns_servers):

    threads = []

    #Create threads that lookup an IP at RIPE
    for sub_list_part in sub_list_parts:
        new_thread = threading.Thread(target=checkip,args=(checked_list,sub_list_part,dns_servers))
        new_thread.start()
        threads.append(new_thread)

    return threads

def get_lines_from_file(input,start,end):

    # This function makes sure that not the entire file is read into memory, be careful when changing this function!
    # This file is "dumb", read_from_file will handle if start and end are possible values

    lines = []

    with open(input) as csv_input:
        all_lines = csv.DictReader(csv_input)
        for i in range(start,end):
            tmp_obj     =   all_lines[i]
            tmp_lookup  =   lookup_obj(tmp_obj,i)
            lines.append(tmp_lookup)

    return lines

def progress(ticker,percent=0, width=40):
    left = width * percent // 100
    right = width - left
    print('\r{}['.format(ticker), '#' * left, ' ' * right, ']',
          f' {percent:.0f}%',
          sep='', end='', flush=True)

def update_ticker(ticker):

    if (ticker == '|'):
        return '-'
    else:
        return '|'

def read_from_file(input,read_list,dicsize,workers,filesize):

    # This function will read rows efficiently into memory and exit when no more lines are present

    file_end = False # Are we at the end of the file

    currentline = 0

    while (!file_end):

        time.sleep(1) # Prevent race against the clock, pauze for a second

        end = 0

        if (currentline >= filesize): # Is this the last set?

            end = filesize
            file_end = True

        else:

            end = currentline + dicsize

        new_dict = get_lines_from_file(input,currentline,end)

        read_list.put(new_dict)

        currentline = end

def write_to_file(input,checked_list,lookup_done_token,file_length):

    threads_done        = False             #   Are the worker threads done?
    progression_counter = 0                 #   This variable is used to give feedback on the progression to the user
    output_file         = ''                #   Variable to add the lookups to
    ticker              = '-'               #   Speed indicator

    #Split input
    base_dir        = os.path.dirname(input)
    file            = os.path.splitext(os.path.basename(input))
    file_name       = file[0]
    file_extension  = file[1]

    output_directory = '{}/{}'.format(base_dir,file_name)

    os.system('mkdir -p {}'.format(output_directory))
    os.system('mkdir -p {}/lookups'.format(output_directory))

    epoch_time = int(time.time())

    output = '{}/lookups/{}_{}_lookup_results.json'.format(output_directory,file_name,epoch_time)
    os.system('cp {} {}'.format(input,output))

    #Copy input file to output file, simply to have a start
    copy_command = 'cp {} {}/lookups/{}_lookup_original.json'.format(input,output_directory,file_name)
    os.system(copy_command)

    #Open file
    with open(output) as json_output:
        output_file = json.load(json_output)

    #Write progression to file and update CLI counter
    while (threads_done == False):

        changes = False #Only write to disk when there are changes

        #Alter file based on lookups
        while not checked_list.empty():
            ticker = update_ticker(ticker) #Update ticker for speed indication
            changes = True
            tmp_result = checked_list.get()
            i = tmp_result[0]
            json_result = tmp_result[1]
            output_file[i] = json_result
            progression_counter +=1

        progression_percentage = math.floor((progression_counter/file_length)*100)
        progress(ticker,progression_percentage)

        #Check if workers threads are done
        if not lookup_done_token.empty():
            threads_done = lookup_done_token.get()

    # All threads are done, now loop through it until all are done
    while not checked_list.empty():
        ticker = update_ticker(ticker) #Update ticker for speed indication
        tmp_result = checked_list.get()
        i = tmp_result[0]
        json_result = tmp_result[1]
        output_file[i] = json_result

    #Write to the output file
    with open(output,'w') as new_file:
        json.dump(output_file,new_file, indent=4)

    progress(u'\u2713',100)


def wait_for_threads(threads):

    for t in threads:
        t.join()

def analyse_data(input,workers,dicsize):

    # Initialisation

    with open(input) as tmp:
        filesize = sum(1 for _ in tmp)

    filesize -= filesize #correcting for first line, this line gives the names of the columns

    print ('The file contains {} lines'.format(filesize))

    start = time.time() #Start keeping track of the time

    read_list           = queue.Queue() # Items that have been read from the file that needs to be checked
    checked_list        = queue.Queue() # Items in this list have been checked and will be written to the disk
    lookup_done_token   = queue.Queue() # This queue will be use to signal the file writer when all other workers are done

    # Start threads

    file_reader_thread = threading.Thread(target=read_from_file,args=(input,read_list,dicsize,workers,filesize)) # This thread will read the data from the file in memory

    threads = create_workers(read_list,checked_list) #Create threads that lookup an IP at RIPE

    file_writer_thread = threading.Thread(target=write_to_file,args=(input,checked_list,lookup_done_token,filesize)) # This thread will write the results to the disk
    file_writer_thread.start()

    # Wait until threads finish

    wait_for_threads(threads) #Wait for worker threads to join back in

    lookup_done_token.put(True) # All worker threads are done, let the writer thread finish and return
    file_writer_thread.join()

    file_reader_thread.join() # Sanity check, normally this thread will finish way before

    # Finish this lookup properly

    end = time.time() #End keeping track of time

    time_difference = math.ceil(end - start)
    print('\nPossible errors in lookup may have occured. Use the report mode to analyse those.')
    print("Lookup is done, it took: {} seconds".format(time_difference)) #Give back the result

