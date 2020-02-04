import datetime
import requests
import json

from django.conf import settings
from django.core.management.base import BaseCommand
from statechanges.models import Block
from statechanges.models import StateChange

# The IPFSstatechange class stores a single IPFS statechange which is not yet in
# the database, but will be processed later.
class IPFSstatechange():
    def __init__(self,hash,previoushash,statechangetype,statechangesubtype):
        '''Stores information about IPFS state changes'''
        self.hash = hash
        self.previoushash = previoushash
        self.statechangetype = statechangetype
        self.statechangesubtype = statechangesubtype

# The StateChangeBatch class stores each state change registered in the
# blockchain. The object need the TX information (timestamp, blocknumber and
# hash) and contains functions to gather additional information like the IPFS
# token.

class StateChangeBatch():
    '''Stores information about StateChangeBatch '''

    def __init__(self, date, blocknumber, hash):
        self.date = date
        self.blocknumber = blocknumber
        self.hash = hash
        self.ipfshash = None
        self.ipfsdata = None
        self.ipfsstatechanges = []

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
            self.ipfsstatechanges.append(IPFSstatechange(
                dataparts[0],
                dataparts[1],
                dataparts[2],
                dataparts[3]
            ))

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
    # Get the IPFS hash for the retrieved statechange batch
    print("Retrieving IPFS hash stored in blocknumber: {}".format(
        statechangebatch.blocknumber))
    statechangebatch.get_ipfshash(
        etherscanapikey
    )
    print("The following hash has been found: {}.".format(
        statechangebatch.ipfshash))

    # Get the IPFS data from the IPFS gateway
    print("Retrieving the IPFS data")
    statechangebatch.get_ipfsdata()
    print("IPFS data found, decoding the data.")

    # Decode the IPFS data to get a readable list with firings and wirings
    statechangebatch.decode_ipfsdata()
    print("IPFS data for block {} has been decoded and stored in the batch "
    "object".format(statechangebatch.blocknumber))
    return None


def get_afterblocknumber():
    # Store the blocknumber from where to search for changes
    try:
        afterblocknumber = (Block.objects.filter(Fullyprocessed=True).order_by(
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
        print("Get tx'es containing IPFS data with " +
              "statechange batches after block {}".format(afterblocknumber))
        statechangebatches = retrieve_statechangebatches(
            etherscanapikey,
            "0x4cd90231a36ba78a253527067f8a0a87a80d60e4",
            afterblocknumber
        )
        print("{} new statechange batches found.".format(
            len(statechangebatches)))

        for statechangebatch in statechangebatches:
            # Check or block exists
            BlockExists = Block.objects.filter(
                pk=statechangebatch.blocknumber).exists()
            # If the block doesn't exist yet import in into the database
            if BlockExists == False:
                print("Add block {} to database".format(
                    statechangebatch.blocknumber))
                Block.objects.create(
                    blocknumber = statechangebatch.blocknumber,
                    date = statechangebatch.date,
                )

            # Store block object in variabel
            block=Block.objects.get(pk=statechangebatch.blocknumber)

            # Process the IPFS data (get data, split it in transactions and
            # store it in the statechangebatchobject)
            process_ipfsdata(
                statechangebatch,
                etherscanapikey
            )

            # Process each state change which has been found in the batch
            for ipfsstatechange in statechangebatch.ipfsstatechanges:
                #Check or the statechange already exist
                statechangeexist = StateChange.objects.filter(
                    hash=ipfsstatechange.hash).exists()
                # Adding state change if doesn't exist
                if statechangeexist == False:
                    print("Adding state change {}".format(
                        ipfsstatechange.hash) +\
                    "to the database, found in block {}".format(
                        statechangebatch.blocknumber))

                    # Create statechange object
                    StateChange.objects.create(
                        hash = ipfsstatechange.hash,
                        previoushash = ipfsstatechange.previoushash,
                        statechangetype = ipfsstatechange.statechangetype,
                        statechangesubtype = ipfsstatechange.statechangesubtype,
                        block = block,
                    )

                    # Update the sum in the blocks (Wouldn't be neccesary
                    # because you can get them from the database), but
                    # the sum amounts are used in different views and therefor
                    # saved in the blocks properties.
                    block.add_totalsum()
                    if (ipfsstatechange.statechangetype == "f"
                    and ipfsstatechange.statechangesubtype == "0"):
                        print(block)
                        block.add_f0()
                    elif (ipfsstatechange.statechangetype == "f"
                    and ipfsstatechange.statechangesubtype == "1"):
                        block.add_f1()
                    elif (ipfsstatechange.statechangetype == "f"
                    and ipfsstatechange.statechangesubtype == "2"):
                        block.add_f2()
                    elif (ipfsstatechange.statechangetype == "f"
                    and ipfsstatechange.statechangesubtype == "3"):
                        block.add_f3()
                    elif (ipfsstatechange.statechangetype == "f"
                    and ipfsstatechange.statechangesubtype == "4"):
                        block.add_f4()
                    elif (ipfsstatechange.statechangetype == "f"
                    and ipfsstatechange.statechangesubtype == "5"):
                        block.add_f5()
                    elif (ipfsstatechange.statechangetype == "f"
                    and ipfsstatechange.statechangesubtype == "6"):
                        block.add_f6()
                    elif (ipfsstatechange.statechangetype == "f"
                    and ipfsstatechange.statechangesubtype == "7"):
                        block.add_f7()
                    elif (ipfsstatechange.statechangetype == "f"
                    and ipfsstatechange.statechangesubtype == "8"):
                        block.add_f8()
                    elif (ipfsstatechange.statechangetype == "f"
                    and ipfsstatechange.statechangesubtype == "9"):
                        block.add_f9()
                    elif (ipfsstatechange.statechangetype == "f"
                    and ipfsstatechange.statechangesubtype == "10"):
                        block.add_f10()
                    elif (ipfsstatechange.statechangetype == "f"
                    and ipfsstatechange.statechangesubtype == "11"):
                        block.add_f11()
                    elif (ipfsstatechange.statechangetype == "f"
                    and ipfsstatechange.statechangesubtype == "12"):
                        block.add_f12()
                    elif (ipfsstatechange.statechangetype == "f"
                    and ipfsstatechange.statechangesubtype == "13"):
                        block.add_f13()
                    elif ipfsstatechange.statechangetype == "w":
                        block.add_w()

            # Set block on fully processed
            block.fullyprocessed = True

            print("Statechange batch found in block " + \
            "{} imported in the database".format(statechangebatch.blocknumber))
