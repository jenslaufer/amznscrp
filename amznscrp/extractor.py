
from . import pageelements
from lxml import html


def extract_product_features(asin, content):
    doc = html.fromstring(content)

    data = {
        'asin': asin,
        'image': pageelements.Product.get_image(doc),
        'name': pageelements.Product.get_name(doc),
        'price': pageelements.Product.get_price_val(doc),
        'currency': pageelements.Product.get_currency(doc),
        'reviews_count': pageelements.Product.get_reviews_count(doc),
        'reviews': pageelements.Product.get_reviews(doc),
        'category_path': pageelements.Product.get_category(doc),
        'category': pageelements.Product.get_top_category(doc),
        'bsr': pageelements.Product.get_bsr(doc),
        'dim_x': pageelements.Product.get_dim_x(doc),
        'dim_y': pageelements.Product.get_dim_y(doc),
        'dim_z': pageelements.Product.get_dim_z(doc),
        'dim_unit': pageelements.Product.get_dim_unit(doc),
        'weight': pageelements.Product.get_weight_val(doc),
        'weight_unit': pageelements.Product.get_weight_unit(doc)
    }

    return data
