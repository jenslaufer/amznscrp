import csv
import requests
import json
import time
import re


class ProductPage:

    WEIGHT_RE = r'([0-9,\.]+) ([a-zA-Z]+)'
    DIM_RE = r'([0-9,\.]+) x ([0-9,\.]+) x ([0-9,\.]+) ([a-zA-Z]+)'

    @staticmethod
    def get_name(doc):
        try:
            XPATH_NAME = '//h1[@id="title"]//text()'
            RAW_NAME = doc.xpath(XPATH_NAME)
            NAME = ' '.join(''.join(RAW_NAME).split()
                            ) if RAW_NAME else None
            return NAME
        except Exception as e:
            return None

    @staticmethod
    def get_image(doc):
        try:
            xpath = '//*[@id="landingImage"]/@data-a-dynamic-image'
            return list(json.loads(doc.xpath(xpath)[0]).keys())[0]

        except Exception:
            return None

    @staticmethod
    def get_top_category(doc):
        try:
            XPATH_CATEGORY = '//a[@class="a-link-normal a-color-tertiary"]//text()'
            RAW_CATEGORY = doc.xpath(XPATH_CATEGORY)
            CATEGORY = RAW_CATEGORY[0].strip() if RAW_CATEGORY else None
            return CATEGORY
        except Exception:
            return None

    @staticmethod
    def get_category(doc):
        try:
            XPATH_CATEGORY = '//a[@class="a-link-normal a-color-tertiary"]//text()'
            RAW_CATEGORY = doc.xpath(XPATH_CATEGORY)
            CATEGORY = ' > '.join(
                [i.strip() for i in RAW_CATEGORY]) if RAW_CATEGORY else None
            return CATEGORY
        except Exception:
            return None

    @staticmethod
    def get_reviews(doc):
        try:
            xpath_reviews = '//*[@id="reviewsMedley"]/div/div[1]/div[1]/div/div/div[2]/div/span/span/a/span//text()'
            raw_reviews = doc.xpath(xpath_reviews)
            reviews = ''.join(
                raw_reviews).strip().replace("\n", " ") if raw_reviews else None
            return float(re.search(r'([0-9,\.]+) ([a-z]+) ([0-9]+) ([a-zA-Z]+)', reviews).group(1).replace(",", "."))
        except Exception:
            return None

    @staticmethod
    def get_bsr(doc):
        try:
            XPATH_RANKS = '//*[@id="SalesRank"]//text()'
            RAW_RANKS = doc.xpath(XPATH_RANKS)
            RANKS = ''.join(
                RAW_RANKS).strip().replace("\n", " ") if RAW_RANKS else None
            return int(re.findall(r'Nr\. ([0-9\.]+)', RANKS)[0].replace(".", ""))
        except Exception:
            return None

    @staticmethod
    def get_dim_x(doc):
        try:
            return int(re.search(ProductPage.DIM_RE, ProductPage.get_dim(doc)).group(1))
        except Exception:
            return None

    @staticmethod
    def get_dim_y(doc):
        try:
            return int(re.search(ProductPage.DIM_RE, ProductPage.get_dim(doc)).group(2))
        except Exception:
            return None

    @staticmethod
    def get_dim_z(doc):
        try:
            return int(re.search(ProductPage.DIM_RE, ProductPage.get_dim(doc)).group(3))
        except Exception:
            return None

    @staticmethod
    def get_dim_unit(doc):
        try:
            return re.search(ProductPage.DIM_RE, ProductPage.get_dim(doc)).group(4)
        except Exception:
            return None

    @staticmethod
    def get_dim(doc):
        try:
            XPATH_DIM = '//*[@id="prodDetails"]/div[2]/div[2]/div[1]/div[2]/div/div/table/tbody/tr[1]/td[2]//text()'
            RAW_DIM = doc.xpath(XPATH_DIM)
            DIM = ''.join(
                RAW_DIM).strip() if RAW_DIM else None
            return DIM
        except Exception:
            return None

    @staticmethod
    def get_weight(doc):
        try:
            XPATH_WEIGHT = '//*[@id="prodDetails"]/div[2]/div[2]/div[1]/div[2]/div/div/table/tbody/tr[2]/td[2]//text()'
            RAW_WEIGHT = doc.xpath(XPATH_WEIGHT)
            WEIGHT = ''.join(
                RAW_WEIGHT).strip() if RAW_WEIGHT else None
            return WEIGHT
        except Exception:
            return None

    @staticmethod
    def get_weight_unit(doc):
        try:
            return re.search(ProductPage.WEIGHT_RE, ProductPage.get_weight(doc)).group(2)
        except Exception:
            return None

    @staticmethod
    def get_weight_val(doc):
        try:
            return float(re.search(ProductPage.WEIGHT_RE, ProductPage.get_weight(doc)).group(1).replace(",", "."))
        except Exception:
            return None

    @staticmethod
    def get_price(doc):
        try:
            xpath_priceblock_ourprice = '//*[@id="priceblock_ourprice"]//text()'
            xpath_price_inside_buybox = '//*[@id="price_inside_buybox"]//text()'
            xpath_olp_sl_new = '//*[@id="olp-sl-new"]/span/span//text()'
            raw_price = doc.xpath(xpath_price_inside_buybox)
            if not raw_price:
                raw_price = doc.xpath(xpath_priceblock_ourprice)
                if not raw_price:
                    raw_price = doc.xpath(xpath_olp_sl_new)
            # print("{}: {}".format(get_name(doc), raw_price))

            price = ' '.join(
                ''.join(raw_price).split()).strip() if raw_price else None

            return price
        except Exception as e:
            return None

    @staticmethod
    def get_price_val(doc):
        try:
            return float(ProductPage.get_price(doc)[4:].replace(",", "."))
        except Exception:
            return None

    @staticmethod
    def get_currency(doc):
        try:
            XPATH_SALE_PRICE = '//*[@id="price_inside_buybox"]//text()'
            RAW_SALE_PRICE = doc.xpath(XPATH_SALE_PRICE)
            SALE_PRICE = ' '.join(
                ''.join(RAW_SALE_PRICE).split()).strip() if RAW_SALE_PRICE else None
            return ProductPage.get_price(doc)[0:3]
        except Exception:
            return None

    @staticmethod
    def get_reviews_count(doc):
        try:
            XPATH_REVIEWS = '//*[@id="acrCustomerReviewText"]//text()'
            RAW_REVIEWS = doc.xpath(XPATH_REVIEWS)
            REVIEWS = ''.join(
                RAW_REVIEWS).strip() if RAW_REVIEWS else None
            if REVIEWS != None:
                REVIEWS = int(re.search(r"([0-9]+)", REVIEWS).group(1))
            return REVIEWS
        except Exception:
            return None


class SearchPage:

    @staticmethod
    def get_products(doc):
        results = []
        lis = doc.xpath('//*[@id="s-results-list-atf"]/li')
        for li in lis:
            asin = SearchPage.get_asin(li)
            name = SearchPage.get_name(li)
            price = SearchPage.get_price(li)
            currency = SearchPage.get_currency(li)
            reviews_count = SearchPage.get_reviews_count(li)
            reviews = SearchPage.get_reviews(li)

            results.append(
                {'asin': asin,
                 'name': name,
                 'price': price,
                 'currency': currency,
                 'reviews': reviews,
                 'reviews_count': reviews_count})

        return results

    @staticmethod
    def get_asin(doc):
        try:
            return doc.get('data-asin')
        except:
            return None

    @staticmethod
    def get_name(doc):
        try:
            elements = doc.xpath('.//h2/@data-attribute')
            if len(elements) >= 1:
                return elements[0]
        except Exception as e:
            return None

    @staticmethod
    def get_price(doc):
        try:
            elements = doc.xpath(
                './/*[@class="a-size-base a-color-price s-price a-text-bold"]/text()')
            if len(elements) >= 1:
                return float(elements[0][4:].strip().replace(",", "."))
        except:
            return None

    @staticmethod
    def get_currency(doc):
        try:
            elements = doc.xpath(
                './/*[@class="a-size-base a-color-price s-price a-text-bold"]/text()')
            if len(elements) >= 1:
                return elements[0][:3].strip()
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def get_reviews_count(doc):
        try:
            elements = doc.xpath(
                './/*[@class="a-size-small a-link-normal a-text-normal"]/text()')
            if len(elements) >= 1:
                return float(elements[0].strip().replace(",", "."))
        except:
            return None

    @staticmethod
    def get_reviews(doc):
        try:
            elements = doc.xpath(
                './/*[@class="a-icon-alt"]/text()')
            if len(elements) >= 2:
                return float(elements[1][:3].strip().replace(",", "."))
        except:
            return None
