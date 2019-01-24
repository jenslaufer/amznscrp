from urllib.parse import quote_plus
import re
import requests
import argparse
from string import ascii_lowercase

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
}


def scrape(keywords):
    base_url = 'https://completion.amazon.co.uk'
    mid = 'A1PA6795UKMFR9'
    lop = 'de_DE'
    uri = '{0}/api/2017/suggestions?lop={1}&mid={2}&alias=aps&prefix={3}'

    results = []
    for kwrd in keywords:
        f_kwrd = quote_plus(kwrd)
        result = s.get(uri.format(base_url, lop, mid, f_kwrd))
        if "Invalid Marketplace ID" in result.text:
            resp = s.get(base_url).text
            mid = re.findall(re.compile(
                r'obfuscatedMarketId:\s"(.*)"'), resp)[0]
            result = s.get(uri.format(mid, f_kwrd))
        results.append(result)

    return results


if __name__ == '__main__':
    s = requests.session()
    s.headers.update(headers)

    parser = argparse.ArgumentParser(
        description='Scrapes keyword suggestions from Amazon Search.')
    parser.add_argument('keywords', metavar='keywords', type=str, nargs='+',
                        help='root keyword')
    parser.add_argument('--alphabet', action='store_true',
                        help='added alphabetical keywords')

    args = parser.parse_args()

    keywords = args.keywords
    if args.alphabet:
        keywords = []
        for keyword in args.keywords:
            for c in ascii_lowercase:
                keywords.append(keyword+" "+c)

    scrape(keywords)
