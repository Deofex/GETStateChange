import datetime
import requests
import json

from django.conf import settings
from django.core.management.base import BaseCommand
from statechanges.models import Block, Ticket, StateChange, Event, AppStatus

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
        #url = "https://gateway.ipfs.io/ipfs/"
        #url = "https://cloudflare-ipfs.com/ipfs/"
        url = "https://ipfs.infura.io/ipfs/"
        url = url + self.ipfshash
        logger.info("IPFS URL: {}".format(url))
        ipfsdata = get_url(url)
        logger.info("IPFS succesfully retrieved, split the data")
        ipfsdata = ipfsdata.splitlines()
        # If the first line of the ipfs data doesn't contains 4 segments than
        # the data is invalid. (It frequently happens that the page is a timeout
        # page instead of statechanges.)
        if len(ipfsdata[0].split(",")) != 4:
            raise Exception('IPFS Data invalid')
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
    '''URL to retrieve an URL'''
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


# The function below retrieves a JSON file from an URL. The function ask the
# content of an URL via the get_URL function and convert to content to the JSON
# format.
def get_json_from_url(url):
    '''Function to retrieve a JSON file from an URL'''
    content = get_url(url)
    js = json.loads(content)
    return js


# The function below retrieves all tx'es which contains pointers to GET state
# changes. The function needs an Etherscan API key to make use of the Etherscan
# API, the Etheureum Registration address which keep track of the tx'es posted
# and the blocknumber which from where to start searching.
def retrieve_statechangebatches(
        etherscanapikey, ethregaddress, afterblocknumber):
    '''Function to retrieve statechange batches'''
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
    '''Function to process IPFS data'''
    # Get the IPFS hash for the retrieved statechange batch
    logger.info("Retrieving IPFS hash from blocknumber: {}".format(
        statechangebatch.blocknumber))
    statechangebatch.get_ipfshash(
        etherscanapikey
    )
    logger.info("The following hash has been found in block {}: {}".format(
        statechangebatch.blocknumber,
        statechangebatch.ipfshash))

    # An error has been made in by GET by posting IPFS links with quotes. These
    # IPFS links has been reposted later and the original have been skipped.
    if statechangebatch.ipfshash.startswith('\''):
        logger.info("ipfshash {} is faulty. It will be ignored".format(
            statechangebatch.ipfshash))
        return 100

    # Get the IPFS data from the IPFS gateway
    logger.info(
        "Retrieving the IPFS data with hash {} from the IPFS Gateway".format(
            statechangebatch.ipfshash
        ))

    # It often happens that the IPFs data wasn't retrieved properly, due to a
    # timeout. The loop below is made so it will retry retrieving the ipfs data
    # when such error occurs.
    for i in range(1,100):
        try:
            statechangebatch.get_ipfsdata()
        except:
            if i == 99:
                logger.error(
                    "99 tries to retrieve IPFS data failed, exit script.")
                raise Exception('IPFS data cannot be retrieved')
            else:
                logger.warning(
                    "Error retrieving IPFS Data with hash:{}" \
                        ", timeout? {} time".format(
                            statechangebatch.ipfshash,i))
                continue
        break

    logger.info(
        "IPFS data with hash {} succesfully retrieved, " \
            "decoding the data.".format(statechangebatch.ipfshash))

    # Decode the IPFS data to get a readable list with firings and wirings
    statechangebatch.decode_ipfsdata()
    logger.info("IPFS data for block {} ".format(
        statechangebatch.blocknumber) +\
    "has been decoded and stored in the batch object")
    return None


def get_afterblocknumber():
    ''''Function to return the first blocknumber which should be imported'''
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
        logger.info("Ticket with hash {} not found, create a new one".format(
            previoushash))
        event = Event.objects.get(hash=previoushash)
        Ticket.objects.create(
            hash = hash,
            event = Event.objects.get(hash=previoushash)
        )
        ticket = Ticket.objects.get(hash=hash)
    else:
        previousstate = StateChange.objects.get(hash=previoushash)
        ticket = previousstate.ticket
        logger.info(
            "Existing ticket found, statechange {} will be added.".format(
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

        # If the ticket is part of the catchall address, add the ticket directly
        # under the catchall ticket, because the statechange isn't part of a
        #  valid chain.
        if ticket.pk == 'catchall':
            previoushash = 'catchall'
            ticket = get_ticket(hash,previoushash)
            firing = '999'

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
        elif firing == "999":
            block.add_f999()
            statechangeobject.ticket.event.add_f999(block.date)


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

def process_statechange(statechange,block):
    '''Add a statechange tot the database'''
    # Create statechange object
    if (statechange.statechangetype == "f"):
        # Create the state change object
        try:
            new_statechange (
                hash = statechange.hash,
                previoushash = statechange.previoushash,
                firing = statechange.statechangesubtype,
                block = block,
                )
        except StateChange.DoesNotExist:
            # When a hash can't be imported this is caused that the previous
            # hash has never been uploaded to IPFS/published in the blockchain.
            # The Statechange is invalid and will be added to the catch all
            # address.
            logger.warning("Failed to add hash {}, in block {}. ".format(
                statechange.hash, block.blocknumber) + \
                "because previous hash can't be found. Moved to catchall."
                )
            new_statechange (
                hash = statechange.hash,
                previoushash = "catchall",
                firing = "999",
                block = block,
                )


    if (statechange.statechangetype == "w"):
        # Create the state change object
        new_event (
            hash = statechange.hash,
            block = block,
        )


def checkcatchallticket():
    '''This function created a catchall evend and ticket, used to store events
    which can't be linked'''
    catchallisavailable = Event.objects.filter(
        hash="TheUnknownStateChangesParadise").exists()
    if catchallisavailable == False:
        block = Block.objects.create(
            blocknumber = "8915534",
            date = datetime.datetime(2020, 6, 17, 4, 1, 39),
            fullyprocessed = True
        )

        event = Event.objects.create(
            hash = "TheUnknownStateChangesParadise",
            block = block ,
            name = "The unknown Statechange paradise",
            lastupdate = block.date,
        )

        ticket = Ticket.objects.create(
            hash = "catchall",
            event = event
        )

        statechangeobject = StateChange.objects.create(
            hash = "catchall",
            previoushash = "TheUnknownStateChangesParadise",
            firing = 999,
            block = block,
            ticket = ticket,
        )

        logger.info("Catch all event is created")


def lockimport():
    '''Lock the database for new statechanges import batches'''
    # Try to get the ImportStateChangesReady setting, if it doesn't exist create
    # it.
    try:
        importstatechangesready = AppStatus.objects.get(
            name="ImportStateChangesReady")
    except:
        AppStatus.objects.create(
            name = "ImportStateChangesReady",
            status = True
        )
        importstatechangesready = AppStatus.objects.get(
            name="ImportStateChangesReady")

    # If the status is ready, set is to false (lock). Otherwise create an
    # exception
    if importstatechangesready.status:
        importstatechangesready.disablestatus()
    else:
        raise Exception('Previous import not finished correctly')


def unlockimport():
    '''Funtion to inlock the database for new statechanges import batches'''
    importstatechangesready = AppStatus.objects.get(
        name="ImportStateChangesReady")
    importstatechangesready.enablestatus()


# this class is called by the managed.py of Django. The class will be used
# to schedule the import of state changes in the Django database.
class Command(BaseCommand):
    '''Import statechanges and import them in the database'''

    def handle(self, *args, **kwargs):
        # lock the import process to avoid multiple imports jobs at the same
        # time
        lockimport()

        # Create catch all event if it doesn't exist yet
        checkcatchallticket()

        # Store the Etherscan API key
        etherscanapikey = settings.ETHERSCANAPIKEY

        # Get the blocknumber from where to continue
        afterblocknumber = get_afterblocknumber()

        # Retrieve all statechange batches from the Ethereum network
        # (block/date/hash)
        logger.info("Get tx'es containing IPFS data with " +
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
            # store it in the statechangebatchobject) (if status = 100) go to
            # the next batch.
            process_ipfsdatastatuscode =  process_ipfsdata(
                statechangebatch,
                etherscanapikey
            )

            if process_ipfsdatastatuscode == 100:
                continue

            block.addipfshash(statechangebatch.ipfshash)

            # Process each state change which has been found in the batch
            statechanges = statechangebatch.ipfsstatechanges

            while any(statechanges):
                # Create an empty lists which contains statechanges which have
                # to be delayed because they are depending on a statechange
                # later in the batch
                statechangestodelay = []

                for statechange in statechanges:
                    dependencyfound = any(x.hash == statechange.previoushash \
                        for x in statechanges)
                    if dependencyfound == True:
                        statechangestodelay.append(statechange)
                    else:
                        process_statechange(statechange,block)

                statechanges = statechangestodelay


            # Set block on fully processed
            block.processed()

            logger.info("Statechange batch found in block " + \
            "{} imported in the database".format(statechangebatch.blocknumber))

        # Unlock import process, to make new import jobs possible
        unlockimport()
