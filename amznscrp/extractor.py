
from . import pageelements
from lxml import html


def extract_product_features(asin, content):
    doc = html.fromstring(content)

    data = {
        'asin': asin,
        'image': pageelements.get_image(doc),
        'name': pageelements.get_name(doc),
        'price': pageelements.get_price_val(doc),
        'currency': pageelements.get_currency(doc),
        'reviews_count': pageelements.get_reviews_count(doc),
        'reviews': pageelements.get_reviews(doc),
        'category_path': pageelements.get_category(doc),
        'category': pageelements.get_top_category(doc),
        'bsr': pageelements.get_bsr(doc),
        'dim_x': pageelements.get_dim_x(doc),
        'dim_y': pageelements.get_dim_y(doc),
        'dim_z': pageelements.get_dim_z(doc),
        'dim_unit': pageelements.get_dim_unit(doc),
        'weight': pageelements.get_weight_val(doc),
        'weight_unit': pageelements.get_weight_unit(doc)
    }

    return data
