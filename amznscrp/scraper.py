import bottlenose
from bs4 import BeautifulSoup
import requests
import os
from os import listdir
import re
from lxml import html
import json
import urllib
import datetime
from . import pageelements
from . import proxy
from . import useragent


def search(api_key, api_secret, affiliate_id, keywords, region='DE', search_index='All', pages=1):
    amazon = bottlenose.Amazon(api_key, api_secret, affiliate_id,
                               Region=region, Parser=lambda text: BeautifulSoup(text, 'xml'))
    asins = []
    for itempage in range(1, (pages+1)):
        results = amazon.ItemSearch(
            Keywords=keywords, SearchIndex=search_index, ItemPage=str(itempage))
        for asin in results.find_all('ASIN'):
            asins.append({'asin': asin.text})

    return asins


def extract_features(source):
    product_data = []
    for filename in listdir(source):
        with open('{}/{}'.format(source, filename), 'r', encoding='utf-8') as f:
            content = f.read()
            doc = html.fromstring(content)

            data = {
                'asin': filename[:-5],
                'image': pageelements.get_image(doc),
                'name': pageelements.get_name(doc),
                'price': pageelements.get_price_val(doc),
                'currency': pageelements.get_currency(doc),
                'reviews_count': pageelements.get_reviews_count(doc),
                'reviews': pageelements.get_reviews(doc),
                'category_path': pageelements.get_category(doc),
                'category': pageelements.get_top_category(doc),
                'bsr': pageelements.get_bsr(doc),
                'dim_x': pageelements.get_dim_x(doc),
                'dim_y': pageelements.get_dim_y(doc),
                'dim_z': pageelements.get_dim_z(doc),
                'dim_unit': pageelements.get_dim_unit(doc),
                'weight': pageelements.get_weight_val(doc),
                'weight_unit': pageelements.get_weight_unit(doc)
            }

            product_data.append(data)
    return product_data


def fetch(asins, region='DE', target="c:/temp/amzniches"):
    proxy_srv = proxy.BonanzaProxy()
    user_agents = useragent.UserAgent()
    if not os.path.exists(target):
        os.makedirs(target)

    if region == 'DE':
        base_url = "http://www.amazon.de"

    for asin in asins:
        filename = '{}/{}.html'.format(target, asin)
        to_fetch = True

        if os.path.exists(filename):
            size = os.path.getsize(filename)
            if size > 10000:
                to_fetch = False

        if to_fetch:
            url = "{}/dp/{}".format(base_url, asin)
            print("Downloading: "+url)
            headers = {
                'User-Agent': user_agents.get()}
            proxies = proxy_srv.get()
            try:
                res = requests.get(url, headers=headers, proxies=proxies)

                with open(filename, 'w', encoding=res.encoding) as file:
                    file.write(res.text)
            except Exception as e:
                print(e)
