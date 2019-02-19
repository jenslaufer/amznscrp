import bottlenose
from bs4 import BeautifulSoup
import requests
import os
from os import listdir
import re
import json
import urllib
import datetime
from urllib.parse import quote_plus


def search_api(api_key, api_secret, affiliate_id, keywords, region='DE', search_index='All', pages=1):
    amazon = bottlenose.Amazon(api_key, api_secret, affiliate_id,
                               Region=region, Parser=lambda text: BeautifulSoup(text, 'xml'))
    asins = []
    for itempage in range(1, (pages+1)):
        results = amazon.ItemSearch(
            Keywords=keywords, SearchIndex=search_index, ItemPage=str(itempage))
        for asin in results.find_all('ASIN'):
            asins.append({'asin': asin.text})

    return asins


def search(keyword, proxy_srv, user_agents):
    s = requests.session()
    headers = {
        'User-Agent': user_agents.get(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    }
    proxies = proxy_srv.get()
    url = "https://www.amazon.de/s/ref=nb_sb_noss_2?__mk_de_DE=%C3%85M%C3%85%C5%BD%C3%95%C3%91&url=search-alias%3Daps&field-keywords={}".format(
        quote_plus(keyword))
    try:
        print("get search page for {}".format(keyword))
        result = s.get(url, headers=headers, proxies=proxies)

        return {"keyword": keyword, "content": result.content}
    except Exception as e:
        print(e)


def fetch(asin, proxy_srv, user_agents, region='DE'):
    if region == 'DE':
        base_url = "http://www.amazon.de"

    url = "{}/dp/{}".format(base_url, asin)
    print("Downloading: "+url)
    headers = {
        'User-Agent': user_agents.get()}
    proxies = proxy_srv.get()
    try:
        res = requests.get(url, headers=headers, proxies=proxies)
        return {"asin": asin, "content": res.text}
    except Exception as e:
        print(e)
