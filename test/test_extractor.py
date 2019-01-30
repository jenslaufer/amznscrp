from amznscrp import extractor
import codecs
from lxml import html
from bs4 import BeautifulSoup


def test_search():
    content = ""
    with codecs.open("test/resources/10b22925-aa3f-46c4-8c6a-228d2863fa05.html", 'r', encoding='utf-8') as f:
        content = f.read()

    doc = html.fromstring(content)
    print("xpath:{}".format(
        len(doc.xpath('//*[@id="s-results-list-atf"]/li'))))

    result = extractor.extract_search_product_features(content)
    print(result)
    assert type(result) == list
    assert len(result) == 20
