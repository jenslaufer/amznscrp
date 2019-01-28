import pandas as pd


class BonanzaProxy:

    def __init__(self, proxyfile):
        self.proxies = pd.read_csv(proxyfile)

    def get(self):
        proxies = {}
        row = self.proxies.sample(1)
        proxy = "http://{}:{}@{}:{}/".format(row.iloc[0]['login'],
                                             row.iloc[0]['password'],
                                             row.iloc[0]['ip'],
                                             row.iloc[0]['port_http'])
        proxies['http'] = proxy
        proxies['https'] = proxy

        return proxies
