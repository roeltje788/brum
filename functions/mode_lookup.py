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
        #    url = 'https://stat.ripe.net/data/routing-status/data.json?resource='+ip
        url = 'https://stat.ripe.net/data/network-info/data.json?resource='+ip
        r = requests.get(url)
        json_response = json.loads(r.content)
        return json_response['data']['prefix']
    except:
        print ('Something went wrong on IP: '+ip)
        return 'invalid'

def check_roa(prefix,asn):

    try:
        if (prefix == ""):
            return 'invalid'

        url = 'https://stat.ripe.net/data/rpki-validation/data.json?resource='+asn+'&prefix='+prefix
        r = requests.get(url)
        json_response = json.loads(r.content)
        return json_response['data']['status']
    except:
        print ('Something went wrong on prefix: '+prefix+' with this asn value: '+asn)
        return 'invalid'

def checkip(checked_list,sub_list_part,dns_servers):

    protected = 0

    for i in sub_list_part:

        ip = ''

        if (dns_servers[i]['ip6_address'] == 'NULL'):
            ip = dns_servers[i]['ip4_address']
        else:
            ip = dns_servers[i]['ip6_address']

        asn = dns_servers[i]['as']
        print ('Checking ip: {} for asn: {}'.format(ip,asn))
        tmp_result = check_roa(lookupip(ip),asn)
        if(tmp_result == "valid"):
            protected+=1

    checked_list.put(protected)

def create_workers(sub_list_part,dns_servers):

    threads = []

    #Create threads that lookup an IP at RIPE
    for sub_list_part in sub_list_parts:
        new_thread = threading.Thread(target=checkip,args=(roa_protected,sub_list_part,dns_servers))
        new_thread.start()
        threads.append(new_thread)

    return threads

def get_servers_from_file(input):

    dns_servers = ''

    with open(input) as json_input:

        dns_servers = json.load(json_input)

    return dns_servers[0]

def wait_for_threads(threads):

    for t in threads:
        t.join()

def analyse_data(input,output,workers):

    workers = 0 #TODO: load workers from json file

    dns_servers = get_servers_from_file(input) #Get servers
    file_length = len(dns_servers)
    print ('The file contains {} rows'.format(file_length))

    start = time.time() #Start keeping check of the time

    checked_list = queue.Queue() # items in this list have been checked and will be written to the disk

    sub_list_parts = list(split(range(file_length), workers)) #Create sublists for workers to analyse

    threads = create_workers(sub_list_part,dns_servers) #Create threads that lookup an IP at RIPE

    #TODO: CREATE THREAD THAT WRITES TO DISK

    wait_for_threads(threads) #Wait for threads to join back

    end = time.time() #End keeping track of time

    time_difference = end - start
    print("Lookup is done, it took:{} seconds",format(time_difference)) #Give back the result

