import pandas as pd
import pkg_resources


class Proxy:
    def __init__(self):
        pass

    def get(self):
        return None


class BonanzaProxy(Proxy):

    def __init__(self, username, password):
        path = 'amznscrp/resources/proxies.csv'
        filepath = pkg_resources.resource_filename(__name__, path)
        self.proxies = pd.read_csv(filepath)
        self.username = username
        self.password = password

    def get(self):
        proxies = {}
        row = self.proxies.sample(1)
        proxy = "http://{}:{}@{}".format(self.username,
                                         self.password,
                                         row.iloc[0]['host'])
        proxies['http'] = proxy
        proxies['https'] = proxy

        return proxies
