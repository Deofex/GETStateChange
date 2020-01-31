import datetime
import requests
import json

from django.conf import settings
from django.core.management.base import BaseCommand
from statechanges.models import Block
from statechanges.models import StateChange

# The StateChangeBatch class stores each state change registered in the blockchain.
# The object need the TX information (timestamp, blocknumber and hash) and
# contains functions to gather additional information like the IPFS token.


class StateChangeBatch():
    '''Stores information about StateChangeBatch '''

    def __init__(self, date, blocknumber, hash):
        self.date = date
        self.blocknumber = blocknumber
        self.hash = hash
        self.ipfshash = None
        self.ipfsdata = None
        self.firing0 = 0
        self.firing1 = 0
        self.firing2 = 0
        self.firing3 = 0
        self.firing4 = 0
        self.firing5 = 0
        self.firing6 = 0
        self.firing7 = 0
        self.firing8 = 0
        self.firing9 = 0
        self.firing10 = 0
        self.firing11 = 0
        self.firing12 = 0
        self.firing13 = 0
        self.wiring = 0
        self.unknown = 0
        self.sumstatechanges = 0

    # The function below retrieves the IPFShash from the blockchain via the
    # Ethernetscan API
    def get_ipfshash(self, etherscanapikey):
        # The txurl is the url pointing to the API and can get TX information
        # from the blockchain.
        txurl = "https://api.etherscan.io/api" + \
            "?module=proxy&action=eth_getTransactionByHash" + \
            "&apikey=" + etherscanapikey + \
            "&txhash="
        # Add the tx hash to the url
        txurl = txurl + self.hash
        # Get the information from the API url in JSON format
        txdata = get_json_from_url(txurl)
        # Store the input data of the TX. The API data contains the encoded
        # IPFs hash
        inputdata = (txdata["result"]["input"])
        # The IPFShash is encoded is in the last 128 bytes. The rows below
        # decode the last 128 hex bytes and remove the trailing whitespace.
        # The IPFShash is stored in the object.
        try:
            ipfshash = (bytearray.fromhex(inputdata[-128:]).decode())
            self.ipfshash = ipfshash.rstrip('\x00')
        except:
            print("Can't get the IPFS token for block " + self.blocknumber)

    # This function retrieves the IPFS data via "https://gateway.ipfs.io/ipfs/"
    # IPFS data contains the details of the state changes.
    def get_ipfsdata(self):
        url = "https://gateway.ipfs.io/ipfs/"
        url = url + self.ipfshash
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
                else:  # An unknown firing. (At this moment there are only 14)
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
def retrieve_statechangebatches(
        etherscanapikey, ethregaddress, afterblocknumber):
    ethregurl = "http://api.etherscan.io/api" + \
        "?module=account&action=txlist" + \
        "&address=" + ethregaddress + \
        "&endblock=99999999&sort=asc" + \
        "&apikey=" + etherscanapikey

    # The startblock is the first block after the blocknumber specified
    startblock = str(int(afterblocknumber) + 1)

    # Add the startblock to the url used to get the tx'es
    ethregurl = ethregurl + "&startblock=" + startblock

    # Get all txés after the blocknumber specified with GET state changes
    # registered on it via the etherscan API.
    txraws = get_json_from_url(ethregurl)

    statechangebatches = []
    # Create a list with StateChangeBatches objects
    for txraw in txraws["result"]:
        timestamp = int(txraw["timeStamp"])
        date = datetime.datetime.fromtimestamp(timestamp)
        statechangebatches.append(StateChangeBatch(
            date,
            txraw["blockNumber"],
            txraw["hash"]
        ))

    # Return the list with theStateChangeBatches objects.
    return statechangebatches


# This function get and decode the IPFS data via the following steps
# 2) For each TX the IPFS hash is retrieved via the Etherscan API
# 3) Via the IPFS gateway the IPFS data is retrieved for the TX
# 4) The data is decoded (seperated in different firings and wirings)
def process_ipfsdata(statechangebatch, etherscanapikey):
    print("Retrieving IPFS hash stored in blocknumber: {}".format(
        statechangebatch.blocknumber))
    # Get the IPFS hash for the retrieved statechange batch
    statechangebatch.get_ipfshash(
        etherscanapikey
    )
    print("The following hash has been found: {}.".format(
        statechangebatch.ipfshash))

    print("Retrieving the IPFS data")
    # Get the IPFS data from the IPFS gateway
    statechangebatch.get_ipfsdata()
    print("IPFS data found, decoding the data.")

    # Decode the IPFS data to get a readable list with firings and wirings
    statechangebatch.decode_ipfsdata()
    print("IPFS data has been decoded. IPFS has been processed")
    return None


def get_afterblocknumber():
    # Store the blocknumber from where to search for changes
    try:
        afterblocknumber = (Block.objects.all().order_by(
            '-blocknumber')[:1].get()).blocknumber
    except:
        print("No blocks been found in the db." +
              "The program will use the default.")
        afterblocknumber = 8915534
        print("except true")

    return afterblocknumber

# this class is called by the managed.py of Django. The class will be used
# to schedule the import of state changes in the Django database.


class Command(BaseCommand):
    '''Import statechanges and import them in the database'''

    def handle(self, *args, **kwargs):
        # Store the Etherscan API key
        etherscanapikey = settings.ETHERSCANAPIKEY

        # Get the blocknumber from where to continue
        afterblocknumber = get_afterblocknumber()

        # Retrieve all statechange batches from the Ethereum network
        # (block/date/hash)
        print("Get tx'es containing IPFS data with" +
              "statechange batches after block {}".format(afterblocknumber))
        statechangebatches = retrieve_statechangebatches(
            etherscanapikey,
            "0x4cd90231a36ba78a253527067f8a0a87a80d60e4",
            afterblocknumber
        )

        for statechangebatch in statechangebatches:
            process_ipfsdata(
                statechangebatch,
                etherscanapikey
            )

            print("Store statechange batch for blocknumber {} in the " +
                  "database.".format(statechangebatch.blocknumber))

            DjangoStateChange.objects.create(
                # date = datetime.datetime(2020, 5, 17)
                date=statechangebatch.date,
                blocknumber=statechangebatch.blocknumber,
                sumstatechanges=statechangebatch.sumstatechanges,
                firings0count=statechangebatch.firing0,
                firings1count=statechangebatch.firing1,
                firings2count=statechangebatch.firing2,
                firings3count=statechangebatch.firing3,
                firings4count=statechangebatch.firing4,
                firings5count=statechangebatch.firing5,
                firings6count=statechangebatch.firing6,
                firings7count=statechangebatch.firing7,
                firings8count=statechangebatch.firing8,
                firings9count=statechangebatch.firing9,
                firings10count=statechangebatch.firing10,
                firings11count=statechangebatch.firing11,
                firings12count=statechangebatch.firing12,
                firings13count=statechangebatch.firing13,
                wiringscount=statechangebatch.wiring,
                unknownscount=statechangebatch.unknown
            )
            print("Statechange batch found in block {} imported in the " +
                  "database".format(statechangebatch.blocknumber))
