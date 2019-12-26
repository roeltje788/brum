from .mode_lookup  import *
from .mode_report  import *

def batch_report(file):

    with open(file) as batch:

        for line in batch:
            if (line == ' ' or line ==  '\n' ):
                continue
            single_file = line.splitlines()[0]

            print ('\n Currently handling file: {}\n'.format(single_file))
            generate_report(single_file)

def batch_lookup(file,workers,lineset):

    with open(file) as batch:

        for line in batch:
            if (line == ' ' or line ==  '\n' ):
                continue
            single_file = line.splitlines()[0]

            print ('\n Currently handling file: {}\n'.format(single_file))
            analyse_data(single_file,workers,lineset)

