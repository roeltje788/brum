# Brum

Checks if an IP-address or domain name is inside of a AS IP-prefix protected by a RPKI certificate 

![alt text](https://live.staticflickr.com/7177/7083455607_7bbb823abe_b.jpg)



## Dependencies

The following packages needs to be installed before Brum can be used:

- python3-dateutil
- faketime
- routinator
- RUST
- netaddr (pip3 install netaddr)

(Ziggy is automatically installed as a submodule)

## Arguments

-d (--date):
    sets the date in Ziggy, this way an IP-address can be checked at a certain moment in time
