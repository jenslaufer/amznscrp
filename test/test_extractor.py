from amznscrp import extractor
import codecs


def test_search():
    with codecs.open("test/resources/10b22925-aa3f-46c4-8c6a-228d2863fa05.html", 'r', encoding='utf-8') as f:
        content = f.read()

        result = extractor.extract_search_product_features("bla", content)
        print(result)

        print([res['name'] for res in result])
        assert type(result) == list
        assert len(result) == 22
