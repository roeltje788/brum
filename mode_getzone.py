####GENERAL#####
import os
import json
import requests
import sys
import getopt
import argparse

def write_zone_to_file(zone,output_file):

    with open(output_file, 'w') as outfile:
        json.dump(zone, outfile)
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

def get_output_file(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument("getroothints",help="Output file for this function")
    parser.add_argument("-o", "--output",help="Output file for this function")
    args = parser.parse_args()
    output = args.output

    return output

def get_zone(url,output):

    zone = download_zone(url)

    write_zone_to_file(zone,output)

def get_root_zone(argv):

    output = get_output_file(argv)

    url = 'https://www.internic.net/domain/root.zone'
    get_zone(url,output)


def get_root_hints(argv):

    output = get_output_file(argv)

    url = 'https://www.internic.net/domain/named.root'
    get_zone(url,output)

