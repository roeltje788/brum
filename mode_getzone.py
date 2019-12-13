####GENERAL#####
import os
import json
import requests

def write_zone_to_file(root_zone,output_file):

    with open(output_file, 'w') as outfile:
        json.dump(root_zone, outfile)
    print ('File written to disk')

def download_zone(url):

    os.system('rm -f ./tmp/*')

    print('Downloading all root servers')

    try:
        r = requests.get(url)

        print('Download complete')
        print('Starting conversion of IANA file')

        file = open('./tmp/root.zone',"w+")
        file.write(r.text)
        file.close()

        os.system('zonefile -p ./tmp/root.zone > ./tmp/root_zone.json')

        zone_json = ''

        with open('./tmp/root_zone.json') as json_file:

            zone_json = json.load(json_file)

        correct_zone_json = []

        for ipv4_zone in zone_json['a']:

            correct_zone_json.append({
                'ns_address':ipv4_zone['name'],
                'ip4_address':ipv4_zone['ip'],
                'ip6_address':'NULL',
            })

        for ipv6_zone in zone_json['aaaa']:

            correct_zone_json.append({
                'ns_address':ipv6_zone['name'],
                'ip6_address':ipv6_zone['ip'],
                'ip4_address':'NULL',
            })

        os.system('rm ./tmp/*') #Empty tmp folder again

        print('Conversion of IANA file is complete')

        return correct_zone_json

    except Exception as e:
        print ("{}".format(e))

def get_zone(url):

    output = input("Where should this file be saved (including file name with .json extension)?: ")

    zone = download_zone(url)

    write_zone_to_file(zone,output)

def get_root_zone(argv):

    url = 'https://www.internic.net/domain/root.zone'
    get_zone(url)


def get_root_hints(argv):

    url = 'https://www.internic.net/domain/named.root'
    get_zone(url)
