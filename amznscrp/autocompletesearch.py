from urllib.parse import quote_plus
import re
import requests
import argparse
import json
from string import ascii_lowercase

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
}


def scrape(keyword):
    s = requests.session()
    s.headers.update(headers)
    base_url = 'https://completion.amazon.co.uk'
    mid = 'A1PA6795UKMFR9'
    lop = 'de_DE'
    uri = '{0}/api/2017/suggestions?lop={1}&mid={2}&alias=aps&prefix={3}'

    f_kwrd = quote_plus(keyword)
    result = s.get(uri.format(base_url, lop, mid, f_kwrd))
    if "Invalid Marketplace ID" in result.text:
        resp = s.get(base_url).text
        mid = re.findall(re.compile(
            r'obfuscatedMarketId:\s"(.*)"'), resp)[0]
        result = s.get(uri.format(mid, f_kwrd))

    return json.loads(result.content)
