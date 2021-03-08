import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from selfbank.items import Article


class SelfbankSpider(scrapy.Spider):
    name = 'selfbank'
    start_urls = ['https://blog.selfbank.es/']

    def parse(self, response):
        categories = response.xpath('//ul[@id="mainmenu"]/li/a/@href').getall()
        yield from response.follow_all(categories, self.parse_category)

    def parse_category(self, response):
        category = response.xpath('//h1[@class="page-title"]//text()').get()

        links = response.xpath('//h2/a/@href').getall()
        yield from response.follow_all(links, self.parse_article, cb_kwargs=dict(category=category))

        next_page = response.xpath('//a[text()="Siguiente "]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse_category)

    def parse_article(self, response, category):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1[@class="entry-title"]//text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//time//text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="entry-content"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('category', category)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
