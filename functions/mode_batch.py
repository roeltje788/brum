def batch_report(file):

    with open(file) as batch:

        for line in batch:
            generate_report(line)

def batch_lookup(file,workers):

    with open(file) as batch:

        for line in batch:
            analyse_data(line,workers)

