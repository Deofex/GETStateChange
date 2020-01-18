import requests
import json

from django.core.management.base import BaseCommand
from statechanges.models import CryptoPrice

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

def get_getprice():
    getpriceurl = "https://api.coingecko.com/api/v3/coins/ethereum/" + \
    "contract/0x8a854288a5976036A725879164Ca3e91d30c6A1B"

    getpricejson = get_json_from_url(getpriceurl)
    getpriceeur = getpricejson["market_data"]["current_price"]["eur"]
    getpriceeur = "{0:.2f}".format(getpriceeur)
    print("The new price of GET is " + str(getpriceeur))
    return getpriceeur


class Command(BaseCommand):
    '''Import statechanges and import them in the database'''
    def handle(self,*args, **kwargs):
        if len(CryptoPrice.objects.filter(name="GET")) == 0:
            print("GET price object is not found")
            CryptoPrice.objects.create(
                name = "GET",
                price_eur = 0
            )
            print("GET price object is created")

        getpriceobject = CryptoPrice.objects.filter(name="GET")[0]
        getprice = get_getprice()
        getpriceobject.updateeurprice(getprice)




