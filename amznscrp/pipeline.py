
import sys
import pandas as pd
import numpy as np
import argparse
import pymongo
import gridfs
import os
import datetime
import time
from sklearn.utils import shuffle
from string import ascii_lowercase
from pathos.multiprocessing import ProcessingPool as Pool
import uuid


def __extract_search_features(extractor, keyword, content):
    try:
        return extractor.extract_search_product_features(keyword, content)
    except Exception as e:
        print("{}".format(e))


def __extract_search_features_wrapper(args):
    return __extract_search_features(*args)


def __scrape_search(scraper, proxy_srv, useragents, keyword):
    return scraper.search(keyword, proxy_srv, useragents)


def __scrape_search_wrapper(args):
    return __scrape_search(*args)


def __scrape_product(scraper, proxy_srv, useragents, asin):
    return scraper.fetch(asin, proxy_srv, useragents)


def __scrape_product_wrapper(args):
    return __scrape_product(*args)


def __extract_features(extractor, estimator, asin, content):
    try:
        features = extractor.extract_product_features(asin, content)

        features['last_modified'] = datetime.datetime.utcnow()

        category = features['category']
        bsr = features['bsr']
        sales = estimator.estimate_sales(bsr, category)
        features['sales'] = sales

        return features

    except Exception as e:
        print("{}: {}".format(asin, e))


def __feature_extractor_wrapper(args):
    return __extract_features(*args)


def scrape_keywords(keywords):
    for keyword in keywords:
        results = [{'parent': keyword['parent'], 'keyword':suggestion['value']}
                   for suggestion in autocompletesearch.scrape(keyword['keyword'], proxy_srv, useragent_srv)['suggestions']]
        for result in results:
            num = keywords_coll.count({'keyword': result['keyword']})
            if num == 0:
                result['last_modified'] = datetime.datetime.utcnow()
                result['is_fetched'] = False
                keywords_coll.replace_one(
                    {'keyword': result['keyword']}, result, True)
    return [keyword['parent'] for keyword in keywords]


def scrape_search(parent_keywords, force=False):
    keywords_df = pd.DataFrame(list(keywords_coll.find(
        {"is_fetched": False, "parent": {"$in": parent_keywords}})))

    params = []
    for key, row in keywords_df.iterrows():
        keyword = row['keyword']

        num = products_coll.count({'keyword': keyword})

        print("{}: {}".format(keyword, num))
        if num == 0 or force:
            try:
                params.append((scraper, proxy_srv, useragent_srv, keyword))
            except Exception as e:
                print(e)

    pool = Pool(20)
    results = pool.map(__scrape_search_wrapper, params)

    for result in results:
        filename = '{}.html'.format(str(uuid.uuid4()))
        keyword_metadata = {}
        keyword_metadata['last_modified'] = datetime.datetime.utcnow()
        keyword_metadata['keyword'] = result['keyword']
        keyword_metadata['is_fetched'] = True
        keyword_metadata['filename'] = filename

        fs.put(result['content'], filename=filename,
               encoding="utf-8", contentType="text/html", doc_type="search")
        keywords_coll.update({'keyword': result['keyword']}, {
            '$set': keyword_metadata})

    keywords_df = pd.DataFrame(list(keywords_coll.find(
        {"filename": {'$exists': True}, "parent": {"$in": parent_keywords}})))
    params = []
    for key, row in keywords_df.iterrows():
        try:
            content = fs.get_last_version(row['filename']).read()
            params.append((extractor, row['keyword'], content))
        except Exception as e:
            print("{}".format(e))

    pool = Pool(20)
    results = pool.map(__extract_search_features_wrapper, params)
    print(results)
    for result in results:
        for product in result:
            product['last_modified'] = datetime.datetime.utcnow()
            products_coll.update_one({'asin': product['asin']}, {
                '$set': product}, False)


def scrape_product_details(parent_keywords):
    keywords_df = pd.DataFrame(
        list(keywords_coll.find({"parent": {"$in": parent_keywords}})))
    products_df = pd.DataFrame(
        list(products_coll.find({"bsr": {'$exists': False}})))
    products_df = pd.merge(
        products_df, keywords_df[['parent', 'keyword']], on="keyword", how="inner")

    params = []
    num = 0
    for key, row in products_df.iterrows():
        asin = row['asin']
        filename = "{}.html".format(asin)
        try:
            fs.get_last_version(filename)
            print("Product {} already scraped.".format(asin))
        except Exception as e:
            params.append((scraper, proxy_srv, useragent_srv, asin))

    pool = Pool(10)
    results = pool.map(__scrape_product_wrapper, params)

    for result in results:
        fs.put(result['content'], filename="{}.html".format(result['asin']),
               encoding="utf-8", contentType="text/html", doc_type="product")

    estimator = SalesEstimator(
        path='./product_search/data/', force_new_model_creation=False, force_teaching=False)

    params = []
    for index, row in products_df.iterrows():
        filename = "{}.html".format(row['asin'])
        asin = filename[:-5]
        try:
            print(asin)
            content = fs.get_last_version(filename).read()
            params.append((extractor, estimator, asin,
                           content))
        except gridfs.errors.NoFile as nf:
            print("no file: {}".format(nf))
            products_coll.remove({'asin': asin})

    start = time.time()
    pool = Pool(20)
    results = pool.map(__feature_extractor_wrapper, params)
    print(time.time() - start)

    for result in results:
        if result != None:
            products_coll.update_one({'asin': result['asin']}, {
                '$set': result}, False)
