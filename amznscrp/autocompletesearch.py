from urllib.parse import quote_plus
import re
import requests
import argparse
import json
from string import ascii_lowercase
from . import useragent, proxy


def scrape(keyword, proxyfile, useragentfile):
    proxy_srv = proxy.BonanzaProxy(proxyfile)
    user_agents = useragent.UserAgent(useragentfile)

    s = requests.session()
    headers = {
        'User-Agent': user_agents.get(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    }
    base_url = 'https://completion.amazon.co.uk'
    mid = 'A1PA6795UKMFR9'
    lop = 'de_DE'
    uri = '{0}/api/2017/suggestions?lop={1}&mid={2}&alias=aps&prefix={3}'

    f_kwrd = quote_plus(keyword)
    result = s.get(uri.format(base_url, lop, mid, f_kwrd), headers=headers,
                   proxies=proxy_srv.get())
    if "Invalid Marketplace ID" in result.text:
        resp = s.get(base_url).text
        mid = re.findall(re.compile(
            r'obfuscatedMarketId:\s"(.*)"'), resp)[0]
        result = s.get(uri.format(mid, f_kwrd), headers=headers,
                       proxies=proxy_srv.get())

    return json.loads(result.content)
