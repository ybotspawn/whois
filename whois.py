__author__ = 'ybot'
from dateutil.parser import parse
import types
import urllib2
import json
import socket
headers = {'Accept': 'application/json'}


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
    customerRef = None
    orgRef = None

def get_by_partial_name(partial_name):
    query = "http://whois.arin.net/rest/customers;name={0}*".format(partial_name.replace(" ", "%20")) # substring space for %20
    json_content = __get_content__(query)
    customers = json_content["customers"]["customerRef"]

    if isinstance(customers, types.ListType):
        responses = map(lambda c: __query_company_link__(c["$"]), customers)
    else:
        responses = []
        responses.append(__query_company_link__(customers["$"]))  # u'http://whois.arin.net/rest/customer/C01123650'

    return responses


def get_by_company(query):
    if "http://" in query:
        return __query_company_link__(query)
    # elif org/COMPNAY works
    # elif customer/COMPANY works


def get_by_host(host):
    ip = socket.gethostbyname(host)
    return get_by_ip_address(ip)


def get_by_ip_address(ipaddress):
    # validate ip address
    query = "http://whois.arin.net/rest/ip/{0}".format(ipaddress)
    json_content = __get_content__(query)
    customer = json_content["net"]
    return __build_whois_response__(customer)


def __query_company_link__(link):
    json_content = __get_content__(link)
    if "org" in json_content:
        return __build_whois_response__(json_content["org"])
    elif "customer" in json_content:
        return __build_whois_response__(json_content["customer"])


def __build_whois_response__(customer):
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
            if "iso3166-1" in customer:
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
    return json.loads(contents)