import os
import sys

############FUNCTIONS##################

def update_ziggy_with_date(new_date):
    #UPDATE ZIGGY

    ziggy_date = os.popen("./ziggy/ziggy.py -c ./ziggy/sample-ziggy.conf -d {} > tmp.txt && grep routinator tmp.txt | cut -d \\' -f2".format(new_date)).read()
#   os.system('./ziggy/ziggy.py -c ./ziggy/sample-ziggy.conf -d {}'.format(new_date))
    print ('New date is set to: '+ziggy_date)
    #SET DATE IN FILE
    date = open('.date.txt','w+')
    date.write(new_date+"\n")
    date.write(ziggy_date)
    date.close()



def is_correct_date(requested_date):

    try:
        date = open('.date.txt','r')
        dates = date.read().splitlines()
        read_date = dates[0]
        date.close()

        print ("Ziggy is set to date: {}".format(read_date))

        if read_date != format(requested_date):
            print ("Ziggy will be updated, date is not the same")
            return False
        else:
            print ("Ziggy already has the correct date, no update needed")
            return True
    except FileNotFoundError:
        print ("Ziggy will be updated, no previous date set")
        return False

############MAIN######################

def check_ziggy_with_date(requested_date):

    #requested_date = sys.argv[1] #Requested date by user

    if not is_correct_date(requested_date):
        update_ziggy_with_date(requested_date)

