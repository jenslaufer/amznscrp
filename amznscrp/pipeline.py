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

    def __init__(self,  proxy, useragent, estimator, mongourl="mongodb://localhost"):
        self.proxy = proxy
        self.useragent = useragent
        self.scraper = scraper
        self.extractor = extractor
        self.estimator = estimator
        self.mongourl = mongourl
        self.dbname = 'amazon'
        self.db = MongoClient(self.mongourl)['amazon']

        self.keyword_col_name = 'keywords'
        self.keyword_parent_col_name = 'keyword_parent'
        self.product_col_name = 'products'

    def get_keywords(self, parents):
        keywords_coll = self.db[self.keyword_col_name]
        keywords = [keyword['keyword']
                    for keyword in keywords_coll.find({'parent': {'$in': parents}})]

        return keywords

    def __scrape_product(self, asin):
        import gridfs

        try:
            fs = gridfs.GridFS(self.db)
            result = self.scraper.fetch(
                asin, self.proxy, self.useragent)
            fs.put(result['content'], filename="{}.html".format(result['asin']),
                   encoding="utf-8", contentType="text/html", doc_type="product")

            return result
        except Exception as e:
            print("problem with {}: {}"+e)
            return None

    def __scrape_product_wrapper(self, asin):
        return self.__scrape_product(asin)

    def __extract_features(self, asin, content):
        import uuid
        import gridfs
        import datetime

        products_coll = self.db[self.product_col_name]
        try:
            print("extracting features for {}".format(asin))
            features = self.extractor.extract_product_features(asin, content)

            features['last_modified'] = datetime.datetime.utcnow()

            category = features['category']
            bsr = features['bsr']
            sales = self.estimator.estimate_sales(bsr, category)
            features['sales'] = sales

            features['last_modified'] = datetime.datetime.utcnow()
            products_coll.update_one({'asin': features['asin']}, {
                '$set': features}, True)

            return features

        except Exception as e:
            print("{}: {}".format(asin, e))

    def __feature_extractor_wrapper(self, args):
        return self.__extract_features(*args)

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
            print("scraping search for {} to {}".format(keyword, filename))
            fs.put(result['content'], filename=filename,
                   encoding="utf-8", contentType="text/html", doc_type="search")

            keyword_metadata = {}
            keyword_metadata['last_modified'] = datetime.datetime.utcnow()
            keyword_metadata['filename'] = filename
            keywords_coll.update_one({'keyword': result['keyword']}, {
                '$set': keyword_metadata}, True)
        except Exception as e:
            print("problem scraping search with {}: {}".format(keyword, e))

    def __scrape_search_wrapper(self, keyword):
        return self.__scrape_search(keyword)

    def __extract_searches_features(self, keyword):
        import gridfs
        import datetime
        from pymongo import MongoClient
        db = MongoClient(self.mongourl)['amazon']

        try:
            keywords_coll = db[self.keyword_col_name]
            products_coll = db[self.product_col_name]
            fs = gridfs.GridFS(db)
            keyword_data = keywords_coll.find_one({'keyword': keyword})
            content = fs.get_last_version(keyword_data['filename']).read()
            results = self.extractor.extract_search_product_features(
                keyword, content)
            for result in results:
                result['last_modified'] = datetime.datetime.utcnow()
                print("extracted {} from search {}".format(
                    result['asin'], keyword))
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
        pool = ProcessingPool(10)
        results = pool.map(self.__scrape_search_wrapper, params)
        self.extract_searches_features(keywords)

        return results

    def extract_searches_features(self, keywords):
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

    def scrape_product_details(self, keywords):
        keywords_coll = self.db[self.keyword_col_name]
        products_coll = self.db[self.product_col_name]
        fs = gridfs.GridFS(self.db)

        keywords_df = pd.DataFrame(
            list(keywords_coll.find({"keyword": {"$in": keywords}})))
        products_df = pd.DataFrame(
            list(products_coll.find({"bsr": {'$exists': False}})))
        products_df = pd.merge(
            products_df, keywords_df[['parent', 'keyword']], on="keyword", how="inner")

        params = []
        for key, row in products_df.iterrows():
            asin = row['asin']
            filename = "{}.html".format(asin)
            try:
                fs.get_last_version(filename)
                print("Product {} already scraped.".format(asin))
            except Exception as e:
                params.append(asin)

        pool = ProcessingPool(10)
        pool.map(self.__scrape_product_wrapper, params)

        params = []
        for index, row in products_df.iterrows():
            filename = "{}.html".format(row['asin'])
            asin = filename[:-5]
            try:
                content = fs.get_last_version(filename).read()
                params.append((asin,
                               content))
            except gridfs.errors.NoFile as nf:
                print("no file: {}".format(nf))

        start = time.time()
        pool = ProcessingPool(20)
        pool.map(self.__feature_extractor_wrapper, params)
        print(time.time() - start)


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

    pipeline = Pipeline(proxy_srv, useragent_srv, sales_estimator)

    # Scrape keyword list
    keywords_args = args.keywords
    keyword_groups = []
    for keyword_arg in keywords_args:
        keywords = []
        for c in ascii_lowercase:
            keywords.append(keyword_arg+" "+c)
        keyword_groups.append({'parent': keyword_arg, 'keywords': keywords})

    # pipeline.scrape_keywords(keyword_groups)

    keywords = pipeline.get_keywords(keywords_args)

    # pipeline.scrape_searches(keywords)

    pipeline.scrape_product_details(keywords)
