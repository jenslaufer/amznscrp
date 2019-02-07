import time
from pathos.multiprocessing import ProcessingPool
from . import useragent, proxy, extractor, scraper
from pymongo import MongoClient
import gridfs

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
        params = []
        for keyword in keywords:
            num = self.db['keywords'].count_documents(
                {'keyword': keyword, 'filename': {'$exists': True}})
            if num == 0:
                params.append(keyword)
        pool = ProcessingPool(10)
        return pool.map(self.__scrape_search_wrapper, params)

    def extract_searches_features(self, keywords):
        params = []
        for keyword in keywords:
            params.append(keyword)
        pool = ProcessingPool(20)
        return pool.map(self.__extract_searches_features_wrapper, params)


if __name__ == '__main__':
    proxy_srv = proxy.BonanzaProxy('', '')
    useragent_srv = useragent.UserAgent()
    pipeline = Pipeline(proxy_srv, useragent_srv)
    client = MongoClient()
    db = client['amazon']
    keywords = list(set(pd.DataFrame(list(db['keywords'].find({})))[
        ['keyword']]['keyword'].tolist()))

    pipeline.scrape_searches(keywords)
    pipeline.extract_searches_features(keywords)
