####GENERAL#####
import os
import json
import csv
import requests
import sys
import getopt
import argparse

def write_zone_to_file(zone,output_file):

    json_output = output_file+'.json'
    csv_output  = output_file+'.csv'

    # JSON DUMP
    with open(json_output, 'w') as outfile:
        json.dump(zone, outfile, indent = 4)

    # CSV DUMP
    with open(csv_output, 'w') as outfile:

        csv_writer = csv.DictWriter(outfile, fieldnames=zone[0].keys())
        csv_writer.writeheader() # write header
        csv_writer.writerows(zone)

    # Give feedback to user
    print ('File written to disk')

def download_zone(url):

    os.system('rm -f ./functions/tmp/*')

    print('Downloading all root servers')

    try:
        r = requests.get(url)

        print('Download complete')

        file = open('./functions/tmp/root.zone',"w+")
        file.write(r.text)
        file.close()

        print('Starting conversion of IANA file')

        os.system('zonefile -p ./functions/tmp/root.zone > ./functions/tmp/root_zone.json')

        zone_json = ''

        with open('./functions/tmp/root_zone.json') as json_file:

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

        os.system('rm ./functions/tmp/*') #Empty tmp folder again

        print('Conversion of IANA file is complete')

        return correct_zone_json

    except Exception as e:
        print ("{}".format(e))

def get_zone(url,output):

    zone = download_zone(url)

    write_zone_to_file(zone,output)

def get_root_zone(settings):

    url = 'https://www.internic.net/domain/root.zone'
    output = settings.output+'zone'
    get_zone(url,output)

def get_root_hints(settings):

    url = 'https://www.internic.net/domain/named.root'
    output = settings.output+'hints'
    get_zone(url,output)

