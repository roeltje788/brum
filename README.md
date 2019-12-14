# Brum

Brum is a RPKI deployment analysis tool. It's meant to analyse a zone file with ip-addresses. 

## Workflow

Brum is meant to be used in the following order:

### 0: get zone file
First a file should be created with the zone file to be used by Brum.
There are 3 options:
-Public resolvers: this file comes with brum and are located in the /public_resolvers folder (only the .json is meant for Brum). 
-"IANA root zone" or IANA "root zone hints": these files can be downloaded directly from within Brum (source below). These files will therefore always be up to date. The file can directly be used after downloading in the next step.
-Own zone file: any right formatted .json file with the correct arguments (see below) can be used as input to Brum in the next step.
<br />
<br />
TODO: how should this file look like?

### 1: lookup file
The next step is to lookup a provided file. By lookup is meant to get the certain information (currently: prefix,ASN and if a RPKI certificate is for this prefix) from RIPE. 
These results are then written to a .json file at the desired location.

### 2: create report
The next step is to use the file created in the previous step for analysis. 
Different questions about the RPKI deployment in the list provided will be answered.
Such as, but not limited: How many have RPKI deployed? What is the difference in ipv4 and ipv6?
These answers are written to a .json file. 

TODO: different information depending on what arguments in the supplied file, what arguments?

#### Why write to a .json file?

By writing to a .json file, the answers can be used by another program. 

#### Why the split?

By not combine step 1 and 2. This has been considered, but is not implemented.
Step 1 is network intensive and step 2 is CPU and RAM intensive. 
By this division, step 1 and 2 can be run on a different machine if needed.

In addition, if other functions will be added to Brum in the future, there is no need to ask RIPE again.
The file in step 1 can used again in step 2 giving more information in the second run. 

### 3: read report
The output of step 2 is a .json file this can be used by another program.
To make it more human friendly, this step will take the .json file created in step 2 and generate a readable file with the results.

## Dependencies

The following packages needs to be installed before Brum can be used:

### dns-zonefile 
This program is used to convert the .zone file from IANA to a usable .json file. In order to install this program the following command can be used:
```
npm install dns-zonefile
```
Source:https://www.npmjs.com/package/dns-zonefile

## Arguments

All possible arguments will be shown in the command line with the command: 
```
python3 brum.py -h
```
In short every command will look similar to:
```
python3 brum.py <mode> <additional commands>
```

### Mode: 
This is the mode that Brum will run in. The different modes are:
<br />
<br />
TODO: list modes 

### Additional commands:
These arguments can differ from mode to mode, but generally either or both an input file and an output are required.

## Add function

Currently Brum supports a certain amount of functions as described in the "mode" subsection under Arguments. 
Additional features may be required in the future. These can be added as follows:

TODO: explain how to add a function 

## Sources

This program makes use of several sources:

### Wikipedia public resolvers
There is no official list of public resolvers to test the RPKI deployment. 
There is however a unofficial quiet extensive list on Wikipedia.
This list is premade added to this application. Location is in /public_resolvers in the root folder. 
The .json file can directly be used. The .csv file is purely for convenience and is not meant for this program.
<br />
Source: https://en.wikipedia.org/wiki/Public_recursive_name_server
### IANA
IANA is used to retrieve both the "root zone hints" and the complete "root zone". 
Both can be downloaded from within Brum and both can be used for analysis.
Please be mindful in using this function and don't keep downloading these list for no good reason. 
<br />
Source: https://www.iana.org/domains/root/files
### RIPE database
RIPE is used to analyse a supplied .json in the "lookup" mode. 
Brum will make 2 requests per line in the input .json file. 
Having a large file, will create a relative large amount of requests.
Be mindful in making requests to RIPE, the service is free without any limitations. Let's keep it like that.
If you have any internet restrictions keep the requests in mind. 
They are simple text requests, but can add up if the supplied file is large in size.
<br />
Source: https://stat.ripe.net/docs/data_api/

## JSON

Currently a file used as input to Brum must be of type .json.
Other filetypes such as .yml or .csv are NOT supported.
Please convert first before use.
