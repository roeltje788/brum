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

def checkip(roa_protected,sub_list_part,dns_servers):

    protected = 0

    for i in sub_list_part:

        ip = ''

        if (dns_servers['dns_servers'][i]['ip6_address'] == 'NULL'):
            ip = dns_servers['dns_servers'][i]['ip4_address']
        else:
            ip = dns_servers['dns_servers'][i]['ip6_address']

        asn = dns_servers['dns_servers'][i]['as']
        print ('Checking ip: {} for asn: {}'.format(ip,asn))
        tmp_result = check_roa(lookupip(ip),asn)
        if(tmp_result == "valid"):
            protected+=1

    roa_protected.put(protected)

def analyse_data(argv):

    try:
        opts, args = getopt.getopt(argv,"m:f:w:",["mode=","file=","workers="])
    except getopt.GetoptError:
        print ('use arguments -m and -i')
        sys.exit(2)
    except:
        print ('Some argument is incorrectly set, review the usage of this program in the documentation')

    ip = ''
    asn = ''
    file = ''
    workers = 0

    #Loop through arguments
    for opt, arg in opts:

        if opt in ("-i", "--ip"): #Set IP-address
           ip = arg
        if opt in ("-a", "--asn"): #Set ASN
           asn = arg
        if opt in ("-f", "--file"): #Set source file
           file = arg
        if opt in ("-w", "--workers"): #Set numbers of workers
           workers = arg

    with open(file) as json_file:

        dns_servers = json.load(json_file)

        start = time.time()

        roa_protected = queue.Queue()

        #Process data

        file_length = len(dns_servers['dns_servers'])

        print ('The file contains {} rows'.format(file_length))

        sub_list_parts = list(split(range(file_length), workers))

        threads = []

        for sub_list_part in sub_list_parts:
            new_thread = threading.Thread(target=checkip,args=(roa_protected,sub_list_part,dns_servers))
            new_thread.start()
            threads.append(new_thread)


        for t in threads:
            t.join()

        end = time.time()

        time_difference = end - start
        print('Total lookup took : {}'.format(time_difference))

        # Check thread's return values
        final_result = 0
        while not roa_protected.empty():
            final_result += roa_protected.get()

        #Give back the result
        print("Protected:{}".format(final_result))

        '''
        thread1 = threading.Thread(target=checkip,args=(ip,asn,my_queue))
        thread2 = threading.Thread(target=checkip,args=(ip,asn,my_queue))
        thread3 = threading.Thread(target=checkip,args=(ip,asn,my_queue))
        thread4 = threading.Thread(target=checkip,args=(ip,asn,my_queue))

        thread1.start()
        thread2.start()
        thread3.start()
        thread4.start()

        threads = []

        threads.append(thread1)
        threads.append(thread2)
        threads.append(thread3)
        threads.append(thread4)

        #SYNCHRONOUS EXAMPLE

        syn_start = time.time()

        for i in range(160):
            result = checkip2(ip,asn,my_queue)
            #print (result)

        syn_end = time.time()

        syn_time_difference = syn_end - syn_start
        print('SYNCHRONOUS EXAMPLE: {}'.format(syn_time_difference))
        '''
