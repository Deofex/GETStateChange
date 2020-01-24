import datetime
import requests
import json

from django.conf import settings
from django.core.management.base import BaseCommand
from statechanges.models import BurnTransaction

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


# The function below retrieves a JSON file from an URL which includes GET burn
# transactions.
def import_burntransactions(etherscanapikey,afterblocknumber):
    burnurl = "https://api.etherscan.io/api?" + \
        "module=account&action=tokentx" + \
        "&contractaddress=0x8a854288a5976036a725879164ca3e91d30c6a1b" + \
        "&address=0x0000000000000000000000000000000000000000" + \
        "&sort=asc" + \
        "&apikey=" + etherscanapikey

    # The startblock is the first block after the blocknumber specified
    startblock =  str(int(afterblocknumber) + 1)

    # Add the startblock to the url used to get the burn transactions
    burnurl = burnurl + "&startblock=" + startblock

    # Retrieve the JSON with the GET transactions from the URL
    burntransactionsraw = get_json_from_url(burnurl)

    for burntransaction in burntransactionsraw["result"]:
        timestamp = int(burntransaction["timeStamp"])
        date = datetime.datetime.fromtimestamp(timestamp)
        getburned = float(burntransaction["value"]) /1000000000000000000

        BurnTransaction.objects.create(
            date = date,
            blocknumber = burntransaction["blockNumber"],
            getburned = getburned
        )
        print("Burn transaction found in block %s imported" % (
            burntransaction["blockNumber"]))
    return True

# The class below is  called via manage.py It will update the GET burn
# transactions in the database, so they can be used on the website.
class Command(BaseCommand):
    '''Import GET burn transactions and import them in the database'''
    def handle(self,*args, **kwargs):
        # Store the Etherscan API key
        etherscanapikey = settings.ETHERSCANAPIKEY
        # Store the blocknumber from where to search for changes
        try:
            afterblocknumber = (BurnTransaction.objects.all().order_by(
                '-blocknumber')[:1].get()).blocknumber
        except:
            afterblocknumber=8077320
            print("No earlier block found")

        # Get burn transactions
        burntransactions = import_burntransactions(
            etherscanapikey,
            afterblocknumber)
