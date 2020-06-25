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

# This function is designed to communicate with infura. It will does a post
# API request with the parameters specified
def get_rpc_response(method, infuraapikey, params=[]):
    '''Does an Inufra API request'''
    url = "https://mainnet.infura.io/v3/{}".format(infuraapikey)
    params = params or []
    data = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# This function get all transactions logs via the Infura node
def get_contract_transfers(infuraapikey, etherscanapikey, address,
    decimals=18, from_block=None, to_block=None):
    '''Get a list with logs of ERC20 transfers'''
    from_block = from_block or "0x0"
    # The transfer events on ETH can be identified via the following transfer
    # hash
    transfer_hash = \
        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    params = [{
        "address": address,
        "fromBlock": from_block,
        "toBlock": to_block
    }]
    # Get all eventlogs via Infura, with the above parameters
    logs = get_rpc_response("eth_getLogs", infuraapikey, params)
    logs = logs['result']
    decimals_factor = Decimal("10") ** Decimal("-{}".format(decimals))

    importcountdown = 0
    for log in logs:
        importcountdown = importcountdown + 1
        logger.info("Processing {} of {}".format(importcountdown,len(logs)))
        # If the log entry is something else than the transfer hash, skip
        if log["topics"][0] != transfer_hash:
            continue

        # Add amount/from and the to from the object and add them implicitly
        log["amount"] = Decimal(str(int(log["data"], 16))) * decimals_factor
        log["from"] = log["topics"][1][0:2] + log["topics"][1][26:]
        log["to"] = log["topics"][2][0:2] + log["topics"][2][26:]
        log["timestamp"] = get_blocktimestamp(
            log["blockNumber"], etherscanapikey)
        # Quarter of a second sleep, to not ask to much from the API
        #time.sleep(0.2)
    return logs

# This function query a blocknumber at etherscan and returns the timestamp
def get_blocktimestamp(blocknumber,etherscanapikey):
    '''This function get the timestamp for the block via EtherScan'''
    blocknumber = int(blocknumber,0)
    blockinfourl = "https://api.etherscan.io/api" + \
        "?module=block&action=getblockreward" + \
        "&blockno=" +str(blocknumber) + \
        "&apikey=" + etherscanapikey

    blockinfo = get_json_from_url(blockinfourl)
    return blockinfo["result"]["timeStamp"]

# This function import transactions and stores the information in the database
def import_transactions(infuraapikey, etherscanapikey, getcontractaddress,
    from_block, to_block):
    '''Function to import all information in the database'''

    # Get all the transfers with the needed info
    transfers = get_contract_transfers(infuraapikey,etherscanapikey,
    getcontractaddress,from_block=from_block,to_block=to_block)

    # Process each log seperatly
    for t in transfers:
        # Some transaction will not have a from address and should be skipped
        if not "from" in t:
            continue
        # Convert hex blocknumber to int
        blocknumber = int(t["blockNumber"],0)
        # Add the block to the database if it doesn't exist
        if not Tblock.objects.filter(blocknumber=blocknumber).exists():
            logger.info("Create TBlock {}".format(blocknumber))
            Tblock.objects.create(
                blocknumber = blocknumber,
                date = datetime.datetime.fromtimestamp(int(t["timestamp"]))
            )

        # Add the from and to addresses to the database if they don't exist
        if not GETAddress.objects.filter(address=t["from"]).exists():
            logger.info("Create GET address {}".format(t["from"]))
            GETAddress.objects.create(address=t["from"])
        if not GETAddress.objects.filter(address=t["to"]).exists():
            GETAddress.objects.create(address=t["to"])
            logger.info("Create GET address {}".format(t["to"]))

        # Get the block and addresses
        block = Tblock.objects.get(blocknumber=blocknumber)
        fromaddress = GETAddress.objects.get(address=t["from"])
        toaddress = GETAddress.objects.get(address=t["to"])

        # Add transaction to the database
        logger.info("Create GETTransaction {}".format(t["transactionHash"]))
        GETTransaction.objects.create(
            transactionhash = t["transactionHash"],
            fromaddress = fromaddress ,
            toaddress = toaddress,
            amount = t["amount"],
            block = block,
        )

        # Update the balances of the to and from address
        fromaddress.send(t["amount"])
        toaddress.recieve(t["amount"])

        # Update the last update time of the to and from addresses
        fromaddress.newupdate(block.date)
        toaddress.newupdate(block.date)


# This function is for the first run. It imports multiple transactions batches
def firstrun(infuraapikey, etherscanapikey, getcontractaddress):
    '''Function to run if no earlier transactions have been imported'''
    # If no run has performed before, you can't query everything at all, because
    # Infura won't give so much results back. Using the blocks below will help
    # to import the first blocks in block which aren't to big.
    bulks = [{"fromblock": "0x428FE9","toblock":"0x4F6C67"},
    {"fromblock": "0x4F6C68","toblock":"0x53E6C1"},
    {"fromblock": "0x53E6C2","toblock":"0x667CB1"},
    {"fromblock": "0x667CB2","toblock":"0x9D8949"}]

    for bulk in bulks:
        import_transactions(infuraapikey,etherscanapikey,
        getcontractaddress,bulk["fromblock"],bulk["toblock"])


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
        # Import the Infura and EtherScan API key from the setting file
        infuraapikey = settings.INFURAAPIKEY
        etherscanapikey = settings.ETHERSCANAPIKEY

        # State the GET Protocol contract
        getcontractaddress = "0x8a854288a5976036a725879164ca3e91d30c6a1b"

        # If a transaction with hash
        # 0xf1d0f66fca5189d27f6c322a594fc4a6298145e183d5c73cdf7dd5e11bb6c3ec
        # doesn't exists. (last transaction in the initial batch), run the
        # first run
        ih= "0xf1d0f66fca5189d27f6c322a594fc4a6298145e183d5c73cdf7dd5e11bb6c3ec"
        if not GETTransaction.objects.filter(transactionhash=ih).exists():
            firstrun(infuraapikey,etherscanapikey,getcontractaddress)

        # Determine the blocks which aren't imported yet
        startblock = Tblock.objects.last().blocknumber + 1
        # Maximal 60000 blocks per batch (approx 10 days), to avoid limits
        endblock = startblock + 50000
        # Import next 50000 blocks
        import_transactions(infuraapikey,etherscanapikey,
        getcontractaddress,hex(startblock),hex(endblock))

        # Unlock import process, to make new import jobs possible
        unlockimport()