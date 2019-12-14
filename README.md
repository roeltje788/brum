# Brum

Checks if an IP-address or domain name is inside of a AS IP-prefix protected by a RPKI certificate 

![alt text](https://live.staticflickr.com/7177/7083455607_7bbb823abe_b.jpg)

## Dependencies

The following packages needs to be installed before Brum can be used:

# dns-zonefile 
    (install: npm install dns-zonefile)

## Arguments

All possible arguments will be shown in the command line with the command: python3 brum.py -h
In short every command will start with python3 brum.py <mode> <additional commands>

Mode: this is the mode that Brum will run in. The different modes are:
TODO: list modes 

Additional commands:
These arguments can differ from mode to mode, but generally either or both an input file and a output are required.

## Add function

TODO: explain how to add a function 

## Sources

This program makes use of several sources to make the workflow easier:

#wiki public resolvers
There is no official list of public resolvers to test the RPKI deployment. 
There is however a unofficial quiet extensive list on Wikipedia.
This list is premade added to this application. Location is in /public_resolvers in the root folder. 
The .json file can directly be used. The .csv file is purely for convenience and is not meant for this program.
Source: https://en.wikipedia.org/wiki/Public_recursive_name_server
#IANA
IANA is used to retrieve both the "root zone hints" and the complete "root zone". Both can be downloaded from within Brum.
Please be mindful in using this function and don't keep downloading these list for no good reason. 
Source: https://www.iana.org/domains/root/files
#RIPE database
RIPE is used to analyse a supplied .json in the "lookup" mode. 
Brum will make 2 requests per line in the input .json file. 
Having a large file, will create a relative large amount of requests.
Be mindful in making requests to RIPE, the service is free without any limitations. Let's keep it like that.
If you have any internet restrictions keep the requests in mind. 
They are simple text requests, but can add up if the supplied file is large in size.

