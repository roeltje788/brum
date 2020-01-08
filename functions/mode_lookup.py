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

class lookup_result:
    def __init__(self,prefix,asn):
        self.prefix = prefix
        self.asn = asn

class lookup_obj:
    def __init__(self,line_obj,linenumber):
        self.line_obj = line_obj
        self.linenumber = linenumber

def get_ip(input):

    if (input['ip6_address'] == 'NULL' or input['ip6_address'] == ''):
        return input['ip4_address']
    else:
        return input['ip6_address']

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

        return lookup_result(prefix,asn)
    except:
        return lookup_result('error','error')

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

class thread_obj():

    def __init__(self):
        self.running = True

    def stop(self):
        self.running = False

class worker_obj(thread_obj):

    def run(self,reader_queue,writer_queue):

        while (self.running or not reader_queue.empty()):

            if (not reader_queue.empty()):
                input_line  = reader_queue.get() #Get line

            else:
                continue

            ip          = get_ip(input_line)

            lookup_result  = lookupip(ip)

            input_line['prefix']     = lookup_result.prefix
            input_line['asn']        = lookup_result.asn

            input_line['valid_roa']  = check_roa(lookup_result.prefix,lookup_result.asn)

            writer_queue.put(input_line) #Put line

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

class writer_obj(thread_obj):

    def run(self,output,writer_queue,buffer_writer,filesize):

        progression_counter = 0                 #   This variable is used to give feedback on the progression to the user
        ticker              = '-'               #   Speed indicator
        header              = []                #   The dictionary keys on the first line of the csv file
        first_line          = True              #   Is this the first line we write
        buffer              = []                #   This is the buffer for writing to the disk

        #Write progression to file and update CLI counter
        while (self.running or not writer_queue.empty()):

            tmp_result = {}

            if (not writer_queue.empty()):
                tmp_result = writer_queue.get() # Get a result
            else:
                continue

            if(first_line):

                header = tmp_result.keys()
                with open(output,'a') as output_file:
                    csv_writer = csv.DictWriter(output_file, fieldnames=header)
                    csv_writer.writeheader() # write header

                first_line = False

            else:

                # Update counter and ticker
                ticker = update_ticker(ticker) #Update ticker for speed indication

                progression_counter +=1
                progression_percentage = math.floor((progression_counter/filesize)*100)
                progress(ticker,progression_percentage)

                buffer.append(tmp_result)

                if ( not self.running or len(buffer)>=buffer_writer):

                    #Write to the output file
                    with open(output,'a') as output_file:
                        csv_writer = csv.DictWriter(output_file, fieldnames=header)
                        csv_writer.writerows(buffer)
                        buffer = []

        # Lookup complete
        progress(u'\u2713',100)

def create_workers(reader_queue,writer_queue,workers):

    threads = {}

    #Create threads that lookup an IP at RIPE
    for x in range(1, workers):
        new_worker = worker_obj()
        new_thread = threading.Thread(target=new_worker.run,args=(reader_queue,writer_queue))
        new_thread.start()
        threads[new_worker] = new_thread

    return threads

def thread_handler(reader,writer,workers,tmp_writer,writer_queue):

    reader.join() # Wait until the last line is read

    for t in workers: #Tell all the workers that this is the last set
        t.stop()

    for t in workers: # Wait till all workers have finished there work
        workers[t].join()

    tmp_writer.stop() #Tell the writer thread that this is the last piece of data to write

    writer.join()

def initialize_lookup(input):

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
    os.system('touch {}'.format(output))

    #Create original file
    copy_command = 'cp {} {}/lookups/{}_lookup_original.json'.format(input,output_directory,file_name)
    os.system(copy_command)

    return output

def analyse_data(settings):

    # Initialisation

    filesize = 0

    with open(settings.input) as tmp:
        filesize = sum(1 for line in tmp)

    filesize = filesize - 1 #correcting for first line, this line gives the names of the columns

    print ('The file contains {} lines'.format(filesize))

    start = time.time() #Start keeping track of the time

    output = initialize_lookup(settings.input) # Setup new files and folders on the disk to write to

    reader_queue        = queue.Queue() # Items that have been read from the file that needs to be checked
    writer_queue        = queue.Queue() # Items in this list have been checked and will be written to the disk

    # Start threads

    # This thread will read the data from the file in memory
    reader = threading.Thread(target=reader_obj().run,args=(settings.input,reader_queue,settings.buffer_reader,settings.sleep_reader))
    reader.start()
    # This thread will write the results to the disk
    tmp_writer = writer_obj()
    writer = threading.Thread(target=tmp_writer.run,args=(output,writer_queue,settings.buffer_writer,filesize))
    writer.start()
    # Create threads that lookup an IP at RIPE (getting data from reader_queue and writing to writer_queue)
    workers = create_workers(reader_queue,writer_queue,settings.workers)

    # Handles the above threads in a good manner until all is done
    thread_handler(reader,writer,workers,tmp_writer,writer_queue)

    # Finish this lookup correctly
    end = time.time() #End keeping track of time

    time_difference = math.ceil(end - start)
    print('\nPossible errors in lookup may have occured. Use the report mode to analyse those.')
    print("Lookup is done, it took: {} seconds".format(time_difference)) #Give back the result

