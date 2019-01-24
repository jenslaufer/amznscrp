import urllib
import os
import requests
import json
import altair as alt
import re
import pandas as pd
from get_smarties import Smarties
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn import ensemble
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, make_scorer, r2_score
import pickle


class SalesEstimator:

    def __init__(self, path='./data', force_new_model_creation=False, force_teaching=False):
        self.__one_hot_encoder = Smarties()
        self.__url_templ = "https://junglescoutpro.herokuapp.com/api/v1/sales_estimator?rank={}&category={}&store={}"
        self.__categories = [u'Auto', u'Baby',
                             u'Baumarkt', u'Beauty',
                             u'Bekleidung',
                             u'Beleuchtung',
                             u'Bücher', u'Bürobedarf & Schreibwaren',
                             u'Computer & Zubehör',
                             u'Drogerie & Körperpflege',
                             u'DVD & Blu-ray', u'Elektro-Großgeräte', u'Elektronik',
                             u'Fremdsprachige Bücher',
                             u'Games', u'Garten',
                             u'Gewerbe, Industrie & Wissenschaft',
                             u'Haustier', u'Kamera',
                             u'Koffer, Rucksäcke & Taschen', u'Küche & Haushalt',
                             u'Lebensmittel & Getränke', u'Motorrad',
                             u'Musikinstrumente', u'Schmuck',
                             u'Schuhe & Handtaschen', u'Software',
                             u'Spielzeug', u'Sport & Freizeit', u'Uhren']
        self.__header = {"Accept": "application/json, text/javascript, */*; q=0.01",
                         "Referer": "https://www.junglescout.com/", "Origin": "https://www.junglescout.com",
                         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"}
        self.__ranks = [1, 100, 200, 300, 400, 500, 600, 700,
                        800, 900,  1000, 1200, 1500, 2000, 5000, 10000]
        self.__path = path
        if not os.path.exists(path):
            os.makedirs(path)
        self.__force_new_model_creation = force_new_model_creation
        self.__force_teaching = force_teaching

        self.__load_files()
        self.__data = self.__prepare_data()
        self.__model = self.__teach_model()

    def __load_files(self):
        for rank in self.__ranks:
            for category in self.__categories:
                filename = '{}/{}_{}.json'.format(self.__path, rank, category)
                if (not os.path.exists(filename)) or self.__force_new_model_creation:
                    url = self.__url_templ.format(
                        rank, urllib.parse.quote_plus(category), 'de')
                    print("Downloading: "+url)
                    try:
                        res = requests.get(url, headers=self.__header)
                        with open(filename, 'w', encoding=res.encoding) as file:
                            file.write(res.text)
                    except Exception as e:
                        print(e)

    def __prepare_data(self):
        regex = r'([0-9]+)_([^_]+)\.json'

        rows = []
        for filename in os.listdir(self.__path):
            if filename.endswith(".json"):
                with open('{}/{}'.format(self.__path, filename), 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    groups = re.search(regex, filename)
                    bsr = groups.group(1)
                    category = groups.group(2)
                    noSales = content['estSalesResult']
                    rows.append({'bsr': bsr, 'category': category,
                                 'numberSales': noSales})

        df = pd.DataFrame(rows)
        df = df[df['category'] != 'Motorrad']
        df = df.replace('< 5', 0)
        df = df.replace('N.A.', 0)
        df['numberSales'] = pd.to_numeric(df['numberSales'])
        df['bsr'] = pd.to_numeric(df['bsr'])

        df.replace(['Auto', 'Elektronik', 'Küche & Haushalt'], [
                   'Auto & Motorrad', 'Elektronik & Foto', 'Küche, Haushalt & Wohnen'], inplace=True)

        return df

    def __teach_model(self):
        model_file = '{}/est_sales_predictor.sav'.format(self.__path)
        df = self.__data
        test_df = df[(df.bsr == 300) | (df.bsr == 4000) | (df.bsr == 2000)]
        train_df = df[(df.bsr != 300) & (df.bsr != 5) & (df.bsr != 2000)]

        X_train = self.__one_hot_encoder.fit_transform(
            train_df[['bsr', 'category']])
        y_train = train_df['numberSales']

        X_test = self.__one_hot_encoder.transform(
            test_df[['bsr', 'category']])
        y_test = test_df['numberSales']

        if self.__force_teaching or not os.path.exists(model_file):
            pipe = Pipeline([
                ('regression', None)
            ])

            param_grid = [
                {
                    'regression': [KNeighborsRegressor()],
                    'regression__n_neighbors': [1, 2, 3, 4, 5, 6],
                    'regression__leaf_size': [8, 9, 10, 11, 12],
                    'regression__weights':['uniform', 'distance']
                }]
            grid = GridSearchCV(pipe, param_grid=param_grid,
                                scoring=make_scorer(mean_squared_error))

            grid.fit(X_train, y_train)
            model = grid.best_estimator_

            print(model.score(X_test, y_test))
            pickle.dump(model, open(model_file, 'wb'))
        else:
            model = pickle.load(open(model_file, 'rb'))

        return model

    def estimate_sales(self, df):
        return self.__model.predict(self.__one_hot_encoder.transform(df[['bsr', 'category']]))
