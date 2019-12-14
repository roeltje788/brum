import json

def give_help(argv):

    program_version = ''
    program_supported = ''

    with open('./settings/brum.json') as json_file:

        file                = json.load(json_file)[0]
        program_version     = file['version']
        program_supported   = file['supported']

    print ("\n")
    for key,value in program_supported.items():
        print ("    {} : {}".format(key,value))
    print ("\n")


