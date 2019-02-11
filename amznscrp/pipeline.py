import time
from pathos.multiprocessing import ProcessingPool
from . import useragent, proxy, extractor, scraper, autocompletesearch, salesestimator
import argparse
from pymongo import MongoClient
import gridfs

from string import ascii_lowercase
import datetime
import uuid
import pandas as pd


class Pipeline:

    def __init__(self,  proxy, useragent, mongourl="mongodb://localhost"):
        self.proxy = proxy
        self.useragent = useragent
        self.scraper = scraper
        self.extractor = extractor
        self.db = MongoClient(mongourl)['amazon']

        self.keyword_col_name = 'keywords'
        self.keyword_parent_col_name = 'keyword_parent'
        self.product_col_name = 'products'

    def get_keywords(self, parents):
        keywords_coll = self.db[self.keyword_col_name]
        keywords = [keyword['keyword']
                    for keyword in keywords_coll.find({'parent': {'$in': parents}})]

        return keywords

    def __scrape_search(self, keyword):
        import uuid
        import gridfs
        import datetime
        try:
            keywords_coll = self.db[self.keyword_col_name]
            fs = gridfs.GridFS(self.db)

            result = self.scraper.search(
                keyword, self.proxy, self.useragent)
            filename = '{}.html'.format(str(uuid.uuid4()))
            fs.put(result['content'], filename=filename,
                   encoding="utf-8", contentType="text/html", doc_type="search")

            keyword_metadata = {}
            keyword_metadata['last_modified'] = datetime.datetime.utcnow()
            keyword_metadata['filename'] = filename
            keywords_coll.update_one({'keyword': result['keyword']}, {
                '$set': keyword_metadata}, True)
        except Exception as e:
            print("problem with {}: {}".format(keyword, e))

    def __scrape_search_wrapper(self, keyword):
        return self.__scrape_search(keyword)

    def __extract_searches_features(self, keyword):
        import gridfs
        import datetime

        try:
            keywords_coll = self.db[self.keyword_col_name]
            products_coll = self.db[self.product_col_name]
            fs = gridfs.GridFS(self.db)
            keyword_data = keywords_coll.find_one({'keyword': keyword})
            content = fs.get_last_version(keyword_data['filename']).read()
            results = self.extractor.extract_search_product_features(
                keyword, content)
            for result in results:
                result['last_modified'] = datetime.datetime.utcnow()
                products_coll.update_one({'asin': result['asin'], 'keyword': keyword}, {
                    '$set': result}, True)
        except Exception as e:
            print("failed to extract keyword '{}': {}".format(keyword, e))

    def __extract_searches_features_wrapper(self, keyword):
        return self.__extract_searches_features(keyword)

    def scrape_searches(self, keywords):
        keywords_coll = self.db[self.keyword_col_name]
        params = []
        for keyword in keywords:
            num = keywords_coll.count_documents(
                {'keyword': keyword, 'filename': {'$exists': True}})
            if num == 0:
                params.append(keyword)
        pool = ProcessingPool(1)
        results = pool.map(self.__scrape_search_wrapper, params)
        self.__extract_searches_features(keywords)

        return results

    def __extract_searches_features(self, keywords):
        params = []
        for keyword in keywords:
            params.append(keyword)
        pool = ProcessingPool(20)
        return pool.map(self.__extract_searches_features_wrapper, params)

    def scrape_keywords(self, keywords_groups):
        keywords_coll = self.db[self.keyword_col_name]
        keyword_parents_coll = self.db[self.keyword_parent_col_name]

        for keywords_group in keywords_groups:
            num = keyword_parents_coll.count_documents(
                {"parent": keywords_group['parent']})
            if num == 0:
                for keyword in keywords_group[self.keyword_col_name]:
                    results = [{'parent': keywords_group['parent'], 'keyword':suggestion['value']}
                               for suggestion in autocompletesearch.scrape(keyword,
                                                                           self.proxy, self.useragent)['suggestions']]
                    for result in results:
                        result['last_modified'] = datetime.datetime.utcnow()
                        keywords_coll.replace_one(
                            {'keyword': result['keyword']}, result, True)
                keyword_parents_coll.replace_one(
                    {'parent': keywords_group['parent']}, {'parent': keywords_group['parent']}, True)


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

    pipeline = Pipeline(proxy_srv, useragent_srv)

    # Scrape keyword list
    keywords_args = args.keywords
    keyword_groups = []
    for keyword_arg in keywords_args:
        keywords = []
        for c in ascii_lowercase:
            keywords.append(keyword_arg+" "+c)
        keyword_groups.append({'parent': keyword_arg, 'keywords': keywords})

    pipeline.scrape_keywords(keyword_groups)
    keywords = pipeline.get_keywords(keywords_args)
    pipeline.scrape_searches(keywords)
