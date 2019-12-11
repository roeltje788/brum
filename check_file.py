import json
import os
import sys
import concurrent.futures
from netaddr import IPNetwork,IPAddress

from networking import *

def ask_routinator(ziggy_date,single_server,file_length):

    try:
        tmp_name = single_server['ns_address']+single_server['ip4_address']+single_server['ip6_address']

        os.system('faketime \''+ziggy_date+'\' routinator vrps -n -o ./tmp/'+tmp_name+'.json -f json -a '+single_server['as'])
        progression = os.popen('ls ./tmp/ | wc -l').read().rstrip()
        print("{} of {} is done!".format(progression,file_length))
    except e:
        print (e)

def check_file_with_date_and_file(ziggy_date,file):

    ziggy_time = ziggy_date

    print ('empty ./tmp/ folder')
    os.system('rm ./tmp/*')

    with open(file) as json_file:

        dns_servers = json.load(json_file)
        dns_protected = 0
        dns_unprotected = 0

        file_length = len(dns_servers['dns_servers'])

        print ('The file contains {} rows'.format(file_length))

        executor = concurrent.futures.ProcessPoolExecutor(5)
        futures = [executor.submit(ask_routinator, ziggy_date ,single_server,file_length) for single_server in dns_servers['dns_servers']]
        concurrent.futures.wait(futures)

        for single_server in dns_servers['dns_servers']:

            tmp_name = single_server['ns_address']+single_server['ip4_address']+single_server['ip6_address']

            with open('./tmp/'+tmp_name+'.json') as single_json_file:
                data = json.load(single_json_file)
                protected = False

                roas_found = len(data['roas'])

                for p in data['roas']:

                    in_network = False
                    ip = ''

                    if (single_server['ip6_address'] == 'NULL'):
                        in_network = ip_in_network(single_server['ip4_address'],p['prefix'])
                        ip = single_server['ip4_address']
                    else:
                        in_network = ip_in_network(single_server['ip6_address'],p['prefix'])
                        ip = single_server['ip6_address']

                    if in_network:
                        print ("IP-address: "+ip+" is inside network: "+p['prefix']+" and is protected by RPKI")
                        protected = True
                        dns_protected+=1

                if not protected:
                    print ("IP-address: "+ip+" is not in a protected RPKI AS zone")
                    dns_unprotected+=1

        print ("Protected DNS name servers: {} , Unprotected DNS name servers: {}".format(dns_protected,dns_unprotected))


