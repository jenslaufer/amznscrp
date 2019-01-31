from amznscrp import extractor
import codecs


def test_search():
    with codecs.open("test/resources/d741e464-92aa-494f-84cc-88986b441d54.html", 'r', encoding='utf-8') as f:
        # with codecs.open("test/resources/8a5f1508-bf08-41f7-8d09-731861053b4f.html", 'r', encoding='utf-8') as f:
        content = f.read()

        result = extractor.extract_search_product_features("bla", content)
        print(result)
        assert type(result) == list
        assert len(result) == 22
