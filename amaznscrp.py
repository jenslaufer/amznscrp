from amznscrp import useragent, proxy, extractor, scraper, pipeline, salesestimator
from pymongo import MongoClient
import pandas as pd
import argparse

from string import ascii_lowercase

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Scrapes keyword suggestions from Amazon Search.')
    parser.add_argument('keywords', metavar='keywords', type=str, nargs='+',
                        help='root keyword')

    parser.add_argument('-p', '--password')
    parser.add_argument('-u', '--username')

    args = parser.parse_args()

    username = args.username
    password = args.password

    sales_estimator = salesestimator.SalesEstimator(
        path='./product_search/data/sales_estimator', force_new_model_creation=False, force_teaching=False)

    proxy_srv = proxy.BonanzaProxy(username, password)
    useragent_srv = useragent.UserAgent()

    pipeline = pipeline.Pipeline(proxy_srv, useragent_srv)

    # Scrape keyword list
    keywords_args = args.keywords
    keyword_groups = []
    for keyword_arg in keywords_args:
        keywords = []
        for c in ascii_lowercase:
            keywords.append(keyword_arg+" "+c)
        keyword_groups.append({'parent': keyword_arg, 'keywords': keywords})

    pipeline.scrape_keywords(keyword_groups)
    # pipeline.scrape_searches(keywords)
    # pipeline.extract_searches_features(keywords)
