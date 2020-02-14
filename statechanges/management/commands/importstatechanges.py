import datetime
import requests
import json

from django.conf import settings
from django.core.management.base import BaseCommand
from statechanges.models import Block, Ticket, StateChange, Event

# Configure logger
import logging
logger = logging.getLogger(__name__)


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
            logger.error("Can't get the IPFS token for block " +\
                self.blocknumber)

    # This function retrieves the IPFS data via "https://gateway.ipfs.io/ipfs/"
    # IPFS data contains the details of the state changes.
    def get_ipfsdata(self):
        url = "https://gateway.ipfs.io/ipfs/"
        #url = "https://temporal.cloud/ipfs/"
        url = url + self.ipfshash
        logger.info("IPFS URL: {}".format(url))
        ipfsdata = get_url(url)
        logger.info("IPFS succesfully retrieved, split the data")
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
    logger.info("Retrieving IPFS hash stored in blocknumber: {}".format(
        statechangebatch.blocknumber))
    statechangebatch.get_ipfshash(
        etherscanapikey
    )
    logger.info("The following hash has been found in the IPFS data: {}".format(
        statechangebatch.ipfshash))

    # Get the IPFS data from the IPFS gateway
    logger.info("Retrieving the IPFS data")
    statechangebatch.get_ipfsdata()
    logger.info("IPFS data found, decoding the data.")

    # Decode the IPFS data to get a readable list with firings and wirings
    statechangebatch.decode_ipfsdata()
    logger.info("IPFS data for block {} ".format(
        statechangebatch.blocknumber) +\
    "has been decoded and stored in the batch object")
    return None


def get_afterblocknumber():
    # Store the blocknumber from where to search for changes
    try:
        afterblocknumber = (Block.objects.filter(fullyprocessed=True).order_by(
            '-blocknumber')[:1].get()).blocknumber
    except:
        logger.warning("No blocks has been found in the database. " +\
              "The program will use the default: 8915534.")
        afterblocknumber = 8915534

    return afterblocknumber


def get_ticket(hash,previoushash):
    '''Function which lookup an event'''
    if Event.objects.filter(hash=previoushash).exists():
        logger.info("Ticket not found, create a new one")
        event = Event.objects.get(hash=previoushash)
        Ticket.objects.create(
            hash = hash,
            event = Event.objects.get(hash=previoushash)
        )
        ticket = Ticket.objects.get(hash=hash)
    else:
        previousstate = StateChange.objects.get(hash=previoushash)
        ticket = previousstate.ticket
        logger.info("Existing ticket, statechange will be added: {}".format(
            ticket))

    return ticket


def new_statechange(hash,previoushash,firing,block):
    '''Function to register a new statechange (firing)'''
    #Check or the statechange already exist
    statechangeexist = StateChange.objects.filter(
        hash=hash).exists()

    # Adding state change if doesn't exist
    if statechangeexist == False:
        logger.info("Adding state change {} to the database.".format(hash) +\
        " State change found in block {}".format(block.blocknumber))

        # Lookup the corresponding event
        try:
            ticket = get_ticket(hash,previoushash)
        except StateChange.DoesNotExist as e:
            logger.error("Failed to get the ticket corresponding to hash: " +\
                "{} and previoushash {}".format(hash,previoushash))
            raise(e)

        # Create the state change object
        statechangeobject = StateChange.objects.create(
            hash = hash,
            previoushash = previoushash,
            firing = firing,
            block = block,
            ticket = ticket,
        )

        # Get Event
        event = statechangeobject.ticket.event

        # Update the sum in the blocks (Wouldn't be neccesary
        # because you can get them from the database), but
        # the sum amounts are used in different views and therefor
        # saved in the blocks properties for performance reasons.
        if firing == "0":
            block.add_f0()
            statechangeobject.ticket.event.add_f0(block.date)
        elif firing == "1":
            block.add_f1()
            statechangeobject.ticket.event.add_f1(block.date)
        elif firing == "2":
            block.add_f2()
            statechangeobject.ticket.event.add_f2(block.date)
        elif firing == "3":
            block.add_f3()
            statechangeobject.ticket.event.add_f3(block.date)
        elif firing == "4":
            block.add_f4()
            statechangeobject.ticket.event.add_f4(block.date)
        elif firing == "5":
            block.add_f5()
            statechangeobject.ticket.event.add_f5(block.date)
        elif firing == "6":
            block.add_f6()
            statechangeobject.ticket.event.add_f6(block.date)
        elif firing == "7":
            block.add_f7()
            statechangeobject.ticket.event.add_f7(block.date)
        elif firing == "8":
            block.add_f8()
            statechangeobject.ticket.event.add_f8(block.date)
        elif firing == "9":
            block.add_f9()
            statechangeobject.ticket.event.add_f9(block.date)
        elif firing == "10":
            block.add_f10()
            statechangeobject.ticket.event.add_f10(block.date)
        elif firing == "11":
            block.add_f11()
            statechangeobject.ticket.event.add_f11(block.date)
        elif firing == "12":
            block.add_f12()
            statechangeobject.ticket.event.add_f12(block.date)
        elif firing == "13":
            block.add_f13()
            statechangeobject.ticket.event.add_f13(block.date)

def new_event(hash,block):
    '''Function to register a new statechange (firing)'''
    #Check or the statechange already exist
    eventexist = Event.objects.filter(
        hash=hash).exists()

    # Adding state change if doesn't exist
    if eventexist == False:
        logger.info("Adding event {} to the database.".format(hash) +\
        " Event found in block {}".format(block.blocknumber))

        # Create the state change object
        Event.objects.create(
            hash = hash,
            block = block,
            lastupdate = block.date,
        )

        block.add_w()


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
        logger.warning("Get tx'es containing IPFS data with " +
              "statechange batches after block {}".format(afterblocknumber))
        statechangebatches = retrieve_statechangebatches(
            etherscanapikey,
            "0x4cd90231a36ba78a253527067f8a0a87a80d60e4",
            afterblocknumber
        )
        logger.info("{} new statechange batches found.".format(
            len(statechangebatches)))

        majorfailedipfsimports = []

        for statechangebatch in statechangebatches:
            # Check or block exists
            BlockExists = Block.objects.filter(
                pk=statechangebatch.blocknumber).exists()
            # If the block doesn't exist yet import in into the database
            if BlockExists == False:
                logger.info("Add block {} to database".format(
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

            failedipfsimports = []
            # Process each state change which has been found in the batch
            for ipfsstatechange in statechangebatch.ipfsstatechanges:
                # Create statechange object
                if (ipfsstatechange.statechangetype == "f"):
                    # Create the state change object
                    try:
                        new_statechange (
                            hash = ipfsstatechange.hash,
                            previoushash = ipfsstatechange.previoushash,
                            firing = ipfsstatechange.statechangesubtype,
                            block = block,
                            )
                    except StateChange.DoesNotExist:
                        # When a hash can't be imported this can be caused
                        # because the previous hash is later in the batch
                        # Add it to a failed list, which will be retried later.
                        logger.warning("Failed to add hash {}, ".format(
                            ipfsstatechange.hash) + \
                            "trying again at the end of the block."
                            )
                        failedipfsimports.append(
                            ipfsstatechange
                        )


                if (ipfsstatechange.statechangetype == "w"):
                    # Create the state change object
                    new_event (
                        hash = ipfsstatechange.hash,
                        block = block,
                    )


            # Retry failed ipfs state changes (keep doing this until no )
            # state changes can be imported anymore. IPFS data doesn't seemd to
            # be always in the correct order.
            stateimported = True
            while stateimported == True:
                addtomajorfailedipfsimports = []
                # Set the stateimproted value on false, will be set true again
                # after a succesfull update (after a failure)
                stateimported = False
                # Stateimport failure is a variable which will check or there
                # is a wrong import. If there's 1 failure the state imported
                # might be set to true, to prevent a loop.
                stateimportfailure = False
                # Try to re-import each statechange
                for ipfsstatechange in failedipfsimports:
                    logger.info(
                        "Retrying to add {}".format(ipfsstatechange.hash))
                    try:
                        new_statechange (
                            hash = ipfsstatechange.hash,
                            previoushash = ipfsstatechange.previoushash,
                            firing = ipfsstatechange.statechangesubtype,
                            block = block,
                        )
                        # If a statechange has failed to import before, set the
                        # stateimported variabele on true
                        logger.info("{} is succesfull imported on retry".format(
                            ipfsstatechange.hash))
                        if stateimportfailure == True:
                            stateimported = true

                    except StateChange.DoesNotExist:
                        logger.warning("{} is failing in retry".format(
                            ipfsstatechange.hash))
                        addtomajorfailedipfsimports.append({
                            "hash": ipfsstatechange.hash,
                            "previoushash": ipfsstatechange.previoushash,
                            "block": block
                        })
                        # Set the stateimport failure on true, so the import
                        # will be retried when there's a succesfull add
                        stateimportfailure = True

            # Import the statechanges to the majorfailedipfsimports which went
            # wrong
            for failure in addtomajorfailedipfsimports:
                majorfailedipfsimports.append({
                    "hash": failure["hash"],
                    "previoushash": failure["previoushash"],
                    "block": failure["block"]
                })

            # Set block on fully processed
            block.processed()

            logger.info("Statechange batch found in block " + \
            "{} imported in the database".format(statechangebatch.blocknumber))

        # Print all imports which failed
        for failedipfs in majorfailedipfsimports:
            block = failedipfs["block"]
            logger.error("Niet kunnen importeren:" +\
            "Hash:{}".format(failedipfs["hash"]) + \
            "PreviousHash:{}".format(failedipfs["hash"]) +\
            "Block:{}".format(block.blocknumber))
