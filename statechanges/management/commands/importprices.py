import requests
import json

from django.core.management.base import BaseCommand
from statechanges.models import CryptoPrice

# Configure logger
import logging
logger = logging.getLogger(__name__)


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

# The function below retrieves a JSON file from an URL which includes all price
# data of GET. It extract the EUR price from the JSON file and return this as
# value
def get_getprice():
    getpriceurl = "https://api.coingecko.com/api/v3/coins/ethereum/" + \
    "contract/0x8a854288a5976036A725879164Ca3e91d30c6A1B"

    getpricejson = get_json_from_url(getpriceurl)
    getpriceeur = getpricejson["market_data"]["current_price"]["eur"]
    getpriceeur = "{0:.2f}".format(getpriceeur)
    logger.info("The new price of GET is " + str(getpriceeur))
    return getpriceeur

# The class below is  called via manage.py It will update the GET price in the
# database, so it can be used on the website.
class Command(BaseCommand):
    '''Import statechanges and import them in the database'''
    # The handle database is called via manage.py
    def handle(self,*args, **kwargs):
        # If there's no GET price in the database, add a dummy prive of 0 in it
        if len(CryptoPrice.objects.filter(name="GET")) == 0:
            logger.warning("GET price object is not found")
            CryptoPrice.objects.create(
                name = "GET",
                price_eur = 0
            )
            logger.info("GET price object is created")

        # Get the current GET price object
        getpriceobject = CryptoPrice.objects.filter(name="GET")[0]
        # Get the current GET price
        getprice = get_getprice()
        # Update the GET object with the new GET price
        getpriceobject.updateeurprice(getprice)




