from decimal import Decimal
from django.conf import settings
from django.core.management.base import BaseCommand

import requests, json, time, datetime
from hodlers.models import Tblock,GETAddress,GETTransaction,TAppStatus

# Configure logger
import logging
logger = logging.getLogger(__name__)

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


def import_transactions(etherscanapikey,startblocknr):
    lastblocknumber = startblocknr
    while(lastblocknumber==startblocknr or len(trans["result"]) == 1000):
        # The new lastblocknumber is the last blocknumber which will be
        # processed+ 1 (oterwise the latest block will be imported twice)
        lastblocknumber = lastblocknumber + 1

        # Specify interesting ETH topics
        transfer_hash = \
            "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
        burn_hash = \
            "0x696de425f79f4a40bc6d2122ca50507f0efbeabbff86a84871b7196ab8ea8df7"

        # Get JSON from the lastblocknumber with the transaction hash
        urltrans="https://api.etherscan.io/api?module=logs&action=getLogs&" + \
            "fromBlock=" + str(lastblocknumber) + \
            "&toBlock=latest" + \
            "&address=0x8a854288a5976036a725879164ca3e91d30c6a1b" + \
            "&topic0=" + transfer_hash + \
            "&apikey=" + etherscanapikey
        trans = get_json_from_url(urltrans)

        # Get JSON from the lastblocknumber with the burn hash
        urlburns="https://api.etherscan.io/api?module=logs&action=getLogs&" + \
            "fromBlock=" + str(lastblocknumber) + \
            "&toBlock=latest" + \
            "&address=0x8a854288a5976036a725879164ca3e91d30c6a1b" + \
            "&topic0=" + burn_hash + \
            "&apikey=" + etherscanapikey
        burns = get_json_from_url(urlburns)

        # Determine last block number for the next result
        lastblocknumber = int(trans["result"][-1]["blockNumber"],0)

        logger.info("Amount of new transactions found: {}".format(
            len(trans["result"])))
        logger.info("Amount of burns found: {}".format(
            len(burns["result"])))

        # Remove results with the highest blocknumbers if the length of the results
        # is 1000 (max) to avoid diplicated items in later batches
        if len(trans["result"]) == 1000:
            newresultstrans = [k for k in trans["result"] if int(
                k["blockNumber"],0) !=  lastblocknumber]
            newresultsburns = [k for k in burns["result"] if int(
                k["blockNumber"],0) <  lastblocknumber]
            # -1 from last blocknumber so it will be included in the next batch
            # more transaction might be located in this block
            lastblocknumber = lastblocknumber - 1
        else:
            newresultstrans = [k for k in trans["result"]]
            newresultsburns = [k for k in burns["result"]]

        # Add the results from the transaction and burns to the results list
        for newtrans in newresultstrans:
            add_transtodb(newtrans)
        for newburn in newresultsburns:
            add_transtodb(newburn)


def add_transtodb(trans):
    # Specify interesting ETH topics and burn address
    transfer_hash = \
        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    burn_hash = \
        "0x696de425f79f4a40bc6d2122ca50507f0efbeabbff86a84871b7196ab8ea8df7"
    burnaddress = "0x0000000000000000000000000000000000000000"

    # Convert hex blocknumber to int
    blocknumber = int(trans["blockNumber"],0)

    # Add the block to the database if it doesn't exist
    if not Tblock.objects.filter(blocknumber=blocknumber).exists():
        logger.info("Create TBlock {}".format(blocknumber))
        Tblock.objects.create(
            blocknumber = blocknumber,
            date = datetime.datetime.fromtimestamp(int(trans["timeStamp"],0))
        )
    # Store block to varibele
    block = Tblock.objects.get(blocknumber=blocknumber)

    # Get information from the transfer info
    if trans["topics"][0] == transfer_hash:
        fromaddress = trans["topics"][1][0:2] + trans["topics"][1][26:]
        toaddress = trans["topics"][2][0:2] + trans["topics"][2][26:]
        amount = Decimal(str(int(trans["data"],0))) / 1000000000000000000
    elif trans["topics"][0] == burn_hash:
        data = trans["data"]
        fromaddress = "0x" + data[26:66]
        toaddress = burnaddress
        amount =  Decimal(str(int(data[67:131],16))) / 1000000000000000000

    # Add the from and to addresses to the database if they don't exist
    if not GETAddress.objects.filter(address=fromaddress).exists():
        logger.info("Create GET address: {}".format(fromaddress))
        GETAddress.objects.create(address=fromaddress)
    if not GETAddress.objects.filter(address=toaddress).exists():
        GETAddress.objects.create(address=toaddress)
        logger.info("Create GET address: {}".format(toaddress))

    # Store to and from addresses in variabel
    fromaddress = GETAddress.objects.get(address=fromaddress)
    toaddress = GETAddress.objects.get(address=toaddress)

    # Create the transaction
    GETTransaction.objects.create(
        transactionhash = trans["transactionHash"],
        fromaddress = fromaddress ,
        toaddress = toaddress,
        amount = amount,
        block = block,
    )
    logger.info("Create GET Transaction with hash: {}".format(
        trans["transactionHash"]))


def lockimport():
    '''Lock the database for new statechanges import batches'''
    # Try to get the ImportStateChangesReady setting, if it doesn't exist create
    # it.
    try:
        importstatechangesready = TAppStatus.objects.get(
            name="ImportGETTransactionsReady")
    except:
        TAppStatus.objects.create(
            name = "ImportGETTransactionsReady",
            status = True
        )
        importstatechangesready = TAppStatus.objects.get(
            name="ImportGETTransactionsReady")

    # If the status is ready, set is to false (lock). Otherwise create an
    # exception
    if importstatechangesready.status:
        importstatechangesready.disablestatus()
    else:
        raise Exception(
        'Previous GET Transactions import not finished correctly')


def unlockimport():
    '''Funtion to inlock the database for new statechanges import batches'''
    importstatechangesready = TAppStatus.objects.get(
        name="ImportGETTransactionsReady")
    importstatechangesready.enablestatus()


# Base class, the start of each Django management command
class Command(BaseCommand):
    '''Import GET transactions in the database'''

    def handle(self, *args, **kwargs):
        # lock the import process to avoid multiple imports jobs at the same
        # time
        lockimport()
        # EtherScan API key from the setting file
        etherscanapikey = settings.ETHERSCANAPIKEY

        # If initial mint transaction isn't created, create it
        burnaddress = "0x0000000000000000000000000000000000000000"
        if not GETAddress.objects.filter(address=burnaddress).exists():
            burnaddress = GETAddress.objects.create(address=burnaddress)
            burnaddress.recieve(Decimal("33368773.400000170376363909"))

        # Determine startblock (=lastblock or default =)
        if GETTransaction.objects.last() == None:
            lastblocknumber=4362216
        else:
            lastblocknumber=GETTransaction.objects.last().block.blocknumber

        # Import transactions
        import_transactions(etherscanapikey,lastblocknumber)

        # Unlock import process, to make new import jobs possible
        unlockimport()