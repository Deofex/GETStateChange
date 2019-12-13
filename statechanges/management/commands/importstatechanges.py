import datetime
import requests
import json

from django.conf import settings
from django.core.management.base import BaseCommand
from statechanges.models import StateChange as DjangoStateChange

# The StateChange class stores each state change registered in the blockchain.
# The object need the TX information (timestamp, blocknumber and hash) and
# contains functions to gather additional information like the IPFS token.
class StateChange():
    '''Stores information about StateChanges '''
    def __init__(self, date, blocknumber, hash):
        self.date = date
        self.blocknumber = blocknumber
        self.hash = hash
        self.ipfstoken = None
        self.ipfsdata = None
        self.firing0=0
        self.firing1=0
        self.firing2=0
        self.firing3=0
        self.firing4=0
        self.firing5=0
        self.firing6=0
        self.firing7=0
        self.firing8=0
        self.firing9=0
        self.firing10=0
        self.firing11=0
        self.firing12=0
        self.firing13=0
        self.wiring=0
        self.unknown=0
        self.sumstatechanges=0

    # The function below retrieves the IPFS token from the blockchain via the
    # Ethernetscan API
    def get_ipfstoken(self,etherscanapikey):
        print("Get ipfstoken stored in blocknumber : " + self.blocknumber)
        # The txurl is the url pointing to the API and can get TX information
        # from the blockchain.
        txurl = "https://api.etherscan.io/api" + \
        "?module=proxy&action=eth_getTransactionByHash" + \
        "&apikey=D" + etherscanapikey + \
        "&txhash="
        # Add the tx hash to the url
        txurl = txurl + self.hash
        # Get the information from the API url in JSON format
        txdata = get_json_from_url(txurl)
        # Store the input data of the TX. The API data contains the encoded
        # IPFs hash
        inputdata = (txdata["result"]["input"])
        # The IPFStoken is encoded is in the last 128 bytes. The rows below
        # decode the last 128 hex bytes and remove the trailing whitespace.
        # The IPFS token is stored in the object.
        try:
            ipfstoken = (bytearray.fromhex(inputdata[-128:]).decode())
            self.ipfstoken = ipfstoken.rstrip('\x00')
        except:
            print("Can't get the IPFS token for block " + self.blocknumber)

    # This function retrieves the IPFS data via "https://gateway.ipfs.io/ipfs/"
    # IPFS data contains the details of the state changes.
    def get_ipfsdata(self):
        print("Get IPFS data from the IPFS gateway : " + self.blocknumber)
        url = "https://gateway.ipfs.io/ipfs/"
        url = url + self.ipfstoken
        ipfsdata = get_url(url)
        ipfsdata = ipfsdata.splitlines()
        self.ipfsdata = ipfsdata


    # This function decodes the IPFS data and extract the different type of
    # state changes to the object.
    def decode_ipfsdata(self):
        # For each state change in the IPFS data check what kind of state change
        # have been processed.
        for data in self.ipfsdata:
            # The IPFS data contains multiple segments, seperated bij the comma
            # Split the segements
            dataparts = data.split(",")
            # If the second last data segment is an "f", the state change is
            # a firing. If it's an "W" it's a wiring.
            if dataparts[-2] == "f":
                # There are different firings. The last data segement tells us
                # which firing is processed. Increase the firing which has been
                # processed.
                if dataparts[-1] == "0":
                    self.firing0 += 1
                elif dataparts[-1] == "1":
                    self.firing1 += 1
                elif dataparts[-1] == "2":
                    self.firing2 += 1
                elif dataparts[-1] == "3":
                    self.firing3 += 1
                elif dataparts[-1] == "4":
                    self.firing4 += 1
                elif dataparts[-1] == "5":
                    self.firing5 += 1
                elif dataparts[-1] == "6":
                    self.firing6 += 1
                elif dataparts[-1] == "7":
                    self.firing7 += 1
                elif dataparts[-1] == "8":
                    self.firing8 += 1
                elif dataparts[-1] == "9":
                    self.firing9 += 1
                elif dataparts[-1] == "10":
                    self.firing10 += 1
                elif dataparts[-1] == "11":
                    self.firing11 += 1
                elif dataparts[-1] == "12":
                    self.firing12 += 1
                elif dataparts[-1] == "13":
                    self.firing13 += 1
                else: # An unknown firing. (At this moment there are only 14)
                    self.unknown += 1
            if dataparts[-2] == "w":
                # Increase the wiring state change
                self.wiring += 1

            # Increase the sum of state changes
            self.sumstatechanges += 1


# The function below retrieves the content from an URL which should be specified
# as parameter. The outpuut is the raw data extracted from the URL.
def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

# The function below retrieves a JSON file from an URL. The function ask the
# content of an URL via the get_URL function and convert to content to the JSON
# format.
def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


# The function below retrieves all tx'es which contains pointers to GET state
# changes. The function needs an Etherscan API key to make use of the Etherscan
# API, the Etheureum Registration address which keep track of the tx'es posted
# and the blocknumber which from where to start searching.
def retrieve_statechanges(etherscanapikey, ethregaddress, afterblocknumber):
    ethregurl = "http://api.etherscan.io/api" + \
        "?module=account&action=txlist" + \
        "&address=" + ethregaddress + \
        "&endblock=99999999&sort=asc" + \
        "&apikey=D" + etherscanapikey

    # The startblock is the first block after the blocknumber specified
    startblock =  str(int(afterblocknumber) + 1)

    # Add the startblock to the url used to get the tx'es
    ethregurl = ethregurl + "&startblock=" + startblock

    # Get all txés after the blocknumber specified with GET state changes
    # registered on it via the etherscan API.
    txraws = get_json_from_url(ethregurl)

    statechanges = []
    # Create a list with StateChange objects
    for txraw in txraws["result"]:
        timestamp = int(txraw["timeStamp"])
        date = datetime.datetime.fromtimestamp(timestamp)
        statechanges.append(StateChange(
            date,
            txraw["blockNumber"],
            txraw["hash"]
        ))

    # Return the list with theStateChange objects.
    return statechanges


# This function gives information about the state changes by executing the
# following steps
# 1) Get all TXés state changes after a given block via the Ethereum
#    registration address. The Etherscan API is used for this.
# 2) For each TX the IPFS hash is retrieved via the Etherscan API
# 3) Via the IPFS gateway the IPFS data is retrieved for the TX
# 4) The data is decoded (seperated in different firings and wirings)
def get_statechangeinfo(etherscanapikey,afterblocknumber):
    # Get a list with all state changes
    print("Get all tx'es")
    statechanges = retrieve_statechanges(
        etherscanapikey,
        "0x4cd90231a36ba78a253527067f8a0a87a80d60e4",
        afterblocknumber
    )

    # Process each state change
    for statechange in statechanges:
        # Get the IPFS hash for all retrieved statechanges
        statechange.get_ipfstoken(
            etherscanapikey
        )
        # Get the IPFS data from the IPFS gateway
        statechange.get_ipfsdata()
        # Decode the IPFS data to get a readable list with firings and wirings
        statechange.decode_ipfsdata()

    return statechanges

# this class is called by the managed.py of Django. The class will be used
# to schedule the import of state changes in the Django database.
class Command(BaseCommand):
    '''Import statechanges and import them in the database'''
    def handle(self,*args, **kwargs):
        # Store the Etherscan API key
        etherscanapikey = settings.ETHERSCANAPIKEY
        # Store the blocknumber from where to search for changes
        try:
            afterblocknumber = (DjangoStateChange.objects.all().order_by('-blocknumber')[:1].get()).blocknumber
        except:
            afterblocknumber = 8915534
            print("except true")

        statechangeinfo = get_statechangeinfo(
            etherscanapikey,
            afterblocknumber
        )

        for statechange in statechangeinfo:
            DjangoStateChange.objects.create(
                date = statechange.date, #date = datetime.datetime(2020, 5, 17)
                blocknumber = statechange.blocknumber,
                sumstatechanges = statechange.sumstatechanges,
                firings0count = statechange.firing0,
                firings1count = statechange.firing1,
                firings2count = statechange.firing2,
                firings3count = statechange.firing3,
                firings4count = statechange.firing4,
                firings5count = statechange.firing5,
                firings6count = statechange.firing6,
                firings7count = statechange.firing7,
                firings8count = statechange.firing8,
                firings9count = statechange.firing9,
                firings10count = statechange.firing10,
                firings11count = statechange.firing11,
                firings12count = statechange.firing12,
                firings13count = statechange.firing13,
                wiringscount = statechange.wiring,
                unknownscount = statechange.unknown
            )



