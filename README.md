# Brum

Brum is a RPKI deployment analysis tool. 

## Workflow

Brum has different types of modes. In most of the cases the workflow will look similar to the following order:

### 0: Get zone file
First a file should be created with the zone file to be used by Brum.
There are 3 options:
-Public resolvers: this file comes with brum and are located in the /public_resolvers folder (only the .json is meant for Brum). 
-"IANA root zone" or IANA "root zone hints": these files can be downloaded directly from within Brum (source below). These files will therefore always be up to date. The file can directly be used after downloading in the next step.
-Own zone file: any right formatted .json file with the correct arguments (see below) can be used as input to Brum in the next step.
<br />
<br />

Certain arguments are mandatory, some others are for getting additional arguments in the report function. 
```
Mandatory: ns_address,ip4_address,ip6_address,asn,prefix
```
```
Optional: tot,country
```
- Note: make sure that either the ipv4 or ipv6 address is empty or equal to NULL. In that case Brum will use the other address.
- Note: the tot and country argument can be used seperatly or both. The more arguments are provided the more information the report function will generate later on.
### 1: Lookup file
The next step is to lookup a provided file. By lookup is meant to get the certain information (currently: prefix,ASN and if a RPKI certificate is for this prefix) from RIPE. 
These results are then written to a .json file at the desired location.

### 2: Create report
The next step is to use the file created in the previous step for analysis. 
Different questions about the RPKI deployment in the list provided will be answered.
Such as, but not limited: How many have RPKI deployed? What is the difference in ipv4 and ipv6?
These answers are written to a .json file. 

Depending on which arguments are provided (mandatory and optional arguments in step 0), brum will create a report. If at least one of the mandatory arguments are missing or named differently, Brum will not create a report!
Again, the more arguments given the more information Brum will generate.

#### Why the split?

Step 1 is network intensive and step 2 is CPU and RAM intensive. 
By this division, step 1 and 2 can be run on a different machine if needed.

In addition, if other functions will be added to Brum in the future, there is no need to ask RIPE again.
The file in step 1 can used again in step 2 giving more information in the second run. Especially if the file in step 1 is large the time for step 2 will be significantly less. 

## Dependencies

The following packages needs to be installed before Brum can be used:

### dns-zonefile 
This program is used to convert the .zone file from IANA to a usable .json file. In order to install this program the following command can be used:
```
npm install dns-zonefile
```
Source:https://www.npmjs.com/package/dns-zonefile

### csvtojson
This program helps converting back and forth from csv to json. It's for internal use. 
```
sudo npm install -g csvtojson
```

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
This is the mode that Brum will run in. The mode name can be typed directly after 'python3 brum.py' in order to use this mode. The different modes are:

- **lookup**       :   Brum will analyse a list of ip-addresses (must be a JSON file)
```
Example: python3 brum.py lookup -i <filelocation>
```
Note: <filelocation> should contain the folder,filename and the extension (should always be .csv). Example: /home/user/file.csv
- **batchlookup**  :   Same functionality as mode lookup, but lookup will run for every line in the specified file
```
Example: python3 brum.py batchlookup -i <filelocation>
```
Note: The file should contain one filelocation per line, as would be used in mode lookup (don't end with any delimiter like ',' or '.'. ONLY put the filename)
- **report**       :   Brum will use a file created by *analyse* and generate information about this file
```
Example: python3 brum.py report -i <filelocation> -c <2 letter country code (e.g. NL,US)>
```
Note: <filelocation> file should be of the same structure as in lookup mode. The input file should come from the output from the lookup mode.
- **batchreport**  :   Same functionality as mode report, but report will run for every line in the specified file
```
Example: python3 brum.py batchreport -i <filelocation>
```
Note: put on each line the file to use followed by a comma and the country code to look for (e.g. /home/user/file.csv,NL). Don't use any delimiter!
- **getroothints** :   Brum will download all the Authorative Hint Root servers from IANA
```
Example: python3 brum.py getroothints -o <foldername>
```
Note: only put the folder name here (e.g. /home/user/folder/). Always end with an '/'. The output in the folder will be 1 hints.csv and one hints.json file. Make sure the folder exists!
- **getrootzone**  :   Brum will download all the Authorative Root servers from IANA
```
Example: python3 brum.py getrootzone -o <foldername>
```
Note: only put the folder name here (e.g. /home/user/folder/). Always end with an '/'. The output in the folder will be 1 zone.csv and one zone.json file. Make sure the folder exists
- **domainreport** :   Brum will crossreference a file with an already checked file with DNS servers
```
Example: python3 brum.py domainreport -i <filelocation> -r <referencefile>
```
Note: <filelocation> should have a similar form as in mode 'lookup'. The <referencefile> should be of type .json (any other case similar to mode 'lookup' ). 
- **rootreport**   :   Brum will analyse a root zone file and will give more specific information then the report mode
```
Example: python3 brum.py rootreport -i <filelocation> -r <referencefile>
```
Note: Both <filelocation> and <referencefile> should be of type .csv. 


### Additional commands:
These arguments can differ from mode to mode, but generally either or both an input file and an output are required.

## Adding additional "modes"

Currently Brum supports a certain amount of functions as described in the "mode" subsection under Arguments. 
Additional features may be required in the future. These can be added as follows:

1. Go the functions folder
2. Add another file with the convention mode_<NEW_FUNCTION_NAME>.py
3. Add at least one function to this file
4. go one folder up and open up the brum.py file
5. add the top import the file under the comment "folder:functions"
6. scroll down to the main function in the same file, almost at the end (inside the if else function) is a comment "ADD FUNCTION HERE"
7. create a new elif statement, call the function from step 3 and make sure the settings.mode is equal to the name of the file you created in step 2
8. close the file and go to the settings folder and open the settings.json file
9. This file is used to inform Brum about the new function (Brum will make this function a new mode argument after adding)
10. Go to the 'supported' part and create a new line with a similar structure as the previous lines (as follows '':''). Make sure to end the previous line with an ','! Otherwise Brum will fail. Make sure the name is the same as the file in step 2 and inside the if else statement in step 6
11. Add anything you would like to your newly created file! That's it!

## Sources

This program makes use of several sources:

### TLD list
This list is originally from IANA: https://www.iana.org/domains/root/db
Though since IANA does not provide the list as csv, the following list is used which uses the IANA list as source: https://raw.githubusercontent.com/gh0stwizard/iana-tld-extractor/master/tld.csv
Several TLD's have been added by hand in this file. The file is inside the 'tld' folder.

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

## Supported input filetypes

### CSV
CSV is the supported filetype. This way Brum can read the file line by line and does not have to hold the whole file in memory. 

Note: in some cases a .json file is required

## Supported output filetypes

When using the lookup mode or rootreport mode the output file will be a .csv file. In any other case the output file will be of type .json.

## Supported operating systems

Brum is both created and tested on a Ubuntu 18.04 system. 
Having all dependecies for Brum (see section dependencies) and a python3 interperter will probably work, but a Linux distrobution will probably give the most stable results.

### Python

<p>The minimum version of python is currently: 3.3</p>

## File size limitations

There is no limitations on the filesize. Brum loops through the file and does not store the whole file in memory. This way any filesize can be used (apart from Python or system limitations). The exception to this rule is the report mode. Make sure you have enough RAM in order to handle the larger files. In case there is not enough memory Brum will fail.


