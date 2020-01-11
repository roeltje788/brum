from .mode_lookup  import *
from .mode_report  import *

def batch_report(settings):

    with open(settings.input) as batch:

        for line in batch:
            if (line == ' ' or line ==  '\n' ):
                continue
            single_file = line.splitlines()[0]

            print ('\n Currently handling file: {}\n'.format(single_file))
            generate_report(single_file)

def batch_lookup(settings):

    with open(settings.input) as batch:

        for line in batch:
            if (line == ' ' or line ==  '\n' ):
                continue
            single_file = line.splitlines()[0]

            print ('\n Currently handling file: {}\n'.format(single_file))
            tmp_settings = settings
            tmp_settings.input = single_file
            analyse_data(tmp_settings)

