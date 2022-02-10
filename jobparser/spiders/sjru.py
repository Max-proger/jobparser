import scrapy
from scrapy.http import HtmlResponse

from jobparser.items import JobparserItem


class SjruSpider(scrapy.Spider):
    name = "sjru"
    allowed_domains = ["superjob.ru"]
    start_urls = [
        "https://russia.superjob.ru/vacancy/search/?keywords=Python&period=1&click_from=facet",
        "https://www.superjob.ru/vacancy/search/?keywords=Python&geo%5Br%5D%5B0%5D=3",
    ]

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[contains(@class, 'f-test-button-dalshe')]/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath("///a[contains(@class, 'icMQ_ _6AfZ9 f-test-link')]//@href").getall()
        for link in links:
            yield response.follow(link, callback=self.vacansy_parse)

    def vacansy_parse(self, response: HtmlResponse):
        name = response.xpath("//h1//text()").get()
        salary = response.xpath("//span[contains(@class, '_2Wp8I _3a-0Y _3DjcL _3fXVo')]//text()").getall()
        url = response.url
        yield JobparserItem(name=name, salary=salary, url=url)
