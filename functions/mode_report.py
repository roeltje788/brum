#Questions to answer:
'''
    LOOK AT IP-ADDRESSES NOT DOMAIN NAME

    Basic report (arguments:ns_addresses,ip4_address,ip6_address,asn,prefix):

    - Give overall valid roa
    - Give overall valid roa ipv4 vs ipv6

    Additional argument(s):tot:

    (ignore those without a domain name!!)

    - Give tot number of domains protected (only possible if tot exists)
    - Give top 3 protected and top 3 unprotected domains

    Additional argument(s):country:

    -Difference per country?

    OUTPUT:
    - Generate file with all errors
    - Generate an original file
    - Generate folder for all output
    - Generate file with the above result in .json
    - Generate file from the .json file with the results in human readable version
'''

# Check if a test can run

def validate_basic_test():
    pass

def validate_for_tot_argument():
    pass

def validate_for_country_argument():
    pass

# ALL TESTS

# Basic tests
def valid_roas_in_list(json_file):
    pass

def number_of_errors(json_file):
    pass

# Tests for tot argument


# Tests for country argument


# File management

def get_json_file(input):

    input_file = []

    #Open file
    with open(input) as json_input:
        input_file = json.load(json_output)

    return input_file

# Main program

def generate_report(input):

    json_file = get_json_file(input) #Get the file to make the report for

    print ('Brum will analyse the first line to know how many analysis it can run. Make sure every line has the SAME amount of arguments. Otherwise Brum WILL fail!')

    #Check test (exit if basic test cannot run)
    if (validate_basic_test() == True): #Basic test
        print("All arguments for the basic test exist. Brum will run those tests now")
        valid_roas_in_list(json_file)
        number_of_errors(json_file)
    else:
        sys.exit(1)

    #Tot argument (validation + tests)

    if (validate_for_tot_argument() == True):
        print ("tot argument in input file, will run the tests for this argument now")
    else:
        print ("tot argument not in input file, skipping those tests.")

    #Country argument (validation + tests)

    if (validate_for_tot_argument() == True):
        print ("country argument in input file, will run the tests for this argument now")
    else:
        print ("country argument not in input file, skipping those tests.")

    #Generate output files and write to disk

    base_dir        = os.path.dirname(input)
    file            = os.path.splitext(os.path.basename(input))
    file_name       = file[0]
    file_extension  = file[1]

    output_directory = '{}/{}'.format(base_dir,file_name)

    os.system('mkdir -p {}'.format(output_directory))
    os.system('mkdir -p {}/reports/'.format(output_directory))

    epoch_time = int(time.time())

    output = '{}/reports/{}_{}_report_results.json'.format(output_directory,file_name,epoch_time)
    os.system('cp {} {}'.format(input,output))

    #Copy input file to output file, simply to have a start
    copy_command = 'cp {} {}/reports/{}_original.json'.format(input,output_directory,file_name)
    os.system(copy_command)

