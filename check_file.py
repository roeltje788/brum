import json
import os
import sys
from netaddr import IPNetwork,IPAddress

from networking import *


def check_file_with_date_and_file(ziggy_date,file):

    with open(file) as json_file:

        dns_servers = json.load(json_file)

        dns_protected = 0
        dns_unprotected = 0

        for single_server in dns_servers['dns_servers']:

            os.system('faketime \''+ziggy_date+'\' routinator -q vrps -n -o ./tmp/tmp_output.json -f json -a '+single_server['as'])

            with open('./tmp/tmp_output.json') as json_file:
                data = json.load(json_file)
                protected = False
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


