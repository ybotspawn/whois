__author__ = 'ybot'
# customer_contents = json.loads(contents)
from dateutil.parser import parse
import types
import urllib2
import json
headers = {'Accept': 'application/json'} #'Content-Type': 'application/json',

class WHOISResponse(object):
    handle = None
    name = None
    streetAddress = None
    city = None
    state = None
    postalCode = None
    country = None
    registrationDate = None
    updateDate = None
    ref = None
    comments = None
    startAddress = None
    endAddress = None
    customerName = None

def get_by_partial_name(partial_name):
    query = "http://whois.arin.net/rest/customers;name={0}*".format(partial_name)
    contents = __get_content__(query)
    json_content = json.loads(contents)
    customers = json_content["customers"]["customerRef"]

    # if contents contain more than one, else build whois query
    if len(customers) == 1:
        pass
    else:
        #__parse_query_response__(json_content)
        responses = map(lambda c: __query_customer_link__(c["$"]), customers)
    return responses


# These two should really be the same, is there any syntactic sugar to handle this?
#__query_customer_link__(json_content["$"])  # u'http://whois.arin.net/rest/customer/C01123650'
#__query_customer_link__(c["$"])  # u'http://whois.arin.net/rest/customer/C01123650'
def get_by_ip_address(ipaddress):
    # validate ip address
    # http://whois.arin.net/rest/ip/24.170.225.12
    pass


def __query_customer_link__(customerLink):
    contents = __get_content__(customerLink)
    json_content = json.loads(contents)
    return __build_whois_response__(json_content)


def __build_whois_response__(customer_content):
    customer = customer_content["customer"]
    w = WHOISResponse()
    for prop in dir(WHOISResponse):
        if 'Date' in prop:
            setattr(w, prop, parse(customer[prop]['$']))
        elif prop == "streetAddress" and "streetAddress" in customer:
            line = customer[prop]["line"]
            street = ""
            if isinstance(line, types.ListType):
                for en in line: # lambda this shit
                    street = "{0} {1}".format(street, en["$"])
            else:
                street = line["$"]
            setattr(w, prop, street)
        elif prop == "country":
            setattr(w, prop, customer["iso3166-1"]["code3"]["$"])
        elif prop == "state":
            if "iso3166-2" in customer:
                setattr(w, prop, customer["iso3166-2"]["$"])
        elif not prop.startswith("__"):
            if prop in customer:
                setattr(w, prop, customer[prop]['$'])
    return w


def __get_content__(link):
    req = urllib2.Request(link, None, headers)
    contents = urllib2.urlopen(req).read()
    return contents