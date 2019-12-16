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

def split(seq, num):
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out

def lookupip(ip):

    try:
        url = 'https://stat.ripe.net/data/network-info/data.json?resource='+ip
        r = requests.get(url)
        json_response = json.loads(r.content)

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

    try:

        url = 'https://stat.ripe.net/data/rpki-validation/data.json?resource='+asn+'&prefix='+prefix
        r = requests.get(url)
        json_response = json.loads(r.content)
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

def get_servers_from_file(input):

    dns_servers = ''

    with open(input) as json_input:

        dns_servers = json.load(json_input)

    return dns_servers

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

def write_to_file(input,checked_list,lookup_done_token,file_length):

    threads_done        = False #   Are the worker threads done?
    progression_counter = 0     #   This variable is used to give feedback on the progression to the user
    output_file         = ''    #   Variable to add the lookups to
    ticker              = '-'   #   Speed indicator

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

        ticker = update_ticker(ticker) #Update ticker for speed indication

        changes = False #Only write to disk when there are changes

        #Alter file based on lookups
        while not checked_list.empty():
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

def analyse_data(input,workers):

    dns_servers = get_servers_from_file(input) #Get servers
    file_length = len(dns_servers)
    print ('The file contains {} rows'.format(file_length))

    start = time.time() #Start keeping track of the time

    checked_list        = queue.Queue() # items in this list have been checked and will be written to the disk
    lookup_done_token   = queue.Queue() # this queue will be use to signal the file writer when all other workers are done

    sub_list_parts = list(split(range(file_length), workers)) #Create sublists for workers to analyse

    threads = create_workers(checked_list,sub_list_parts,dns_servers) #Create threads that lookup an IP at RIPE

    file_writer_thread = threading.Thread(target=write_to_file,args=(input,checked_list,lookup_done_token,file_length))
    file_writer_thread.start()

    wait_for_threads(threads) #Wait for worker threads to join back in

    lookup_done_token.put(True)
    file_writer_thread.join()

    end = time.time() #End keeping track of time

    time_difference = math.ceil(end - start)
    print('\nPossible errors in lookup may have occured. Use the report mode to analyse those.')
    print("Lookup is done, it took: {} seconds".format(time_difference)) #Give back the result

