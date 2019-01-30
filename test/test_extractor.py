from amznscrp import extractor
import codecs


def test_search():
    content = ""
    with codecs.open("test/resources/2d1a5dab-0fae-44a6-80fe-77a73d20f674.html", 'r', encoding='utf-8') as f:
        content = f.read()

    result = extractor.extract_search_product_features(content)
    print(result)
    assert type(result) == list
    assert len(result) == 20
