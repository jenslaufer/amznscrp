import amznscrp


def test_scrape_search():
    proxy_srv = amznscrp.proxy.BonanzaProxy("tests/proxylist.csv")
    useragent_srv = amznscrp.useragent.UserAgent("tests/useragents.txt")
    result = amznscrp.scraper.search("usb c kabel", proxy_srv, useragent_srv)
    assert result['keyword'] == "usb c kabel"
    with open("./test/test.html", 'r') as f:
        f.write(result['content'])


test_scrape_search()
