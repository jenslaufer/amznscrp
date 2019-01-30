
from . import pageelements
from lxml import html


def extract_product_features(asin, content):
    doc = html.fromstring(content)

    data = {
        'asin': asin,
        'image': pageelements.ProductPage.get_image(doc),
        'name': pageelements.ProductPage.get_name(doc),
        'price': pageelements.ProductPage.get_price_val(doc),
        'currency': pageelements.ProductPage.get_currency(doc),
        'reviews_count': pageelements.ProductPage.get_reviews_count(doc),
        'reviews': pageelements.ProductPage.get_reviews(doc),
        'category_path': pageelements.ProductPage.get_category(doc),
        'category': pageelements.ProductPage.get_top_category(doc),
        'bsr': pageelements.ProductPage.get_bsr(doc),
        'dim_x': pageelements.ProductPage.get_dim_x(doc),
        'dim_y': pageelements.ProductPage.get_dim_y(doc),
        'dim_z': pageelements.ProductPage.get_dim_z(doc),
        'dim_unit': pageelements.ProductPage.get_dim_unit(doc),
        'weight': pageelements.ProductPage.get_weight_val(doc),
        'weight_unit': pageelements.ProductPage.get_weight_unit(doc)
    }

    return data


def extract_search_product_features(content):
    doc = html.fromstring(content)

    return pageelements.SearchPage.get_products(doc)
