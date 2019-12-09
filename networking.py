from netaddr import IPNetwork,IPAddress


def ip_in_network(ip,network):

    #Example:
    #ip         = 192.168.0.1
    #network    = 192.168.0.0/24

    if IPAddress(ip) in IPNetwork(network):
        return True
    else:
        return False

