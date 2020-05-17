# -*- coding: utf-8 -*-
import scrapy
import re
from pixivsearch.items import PixivsearchItem


class PixivsearchspiderSpider(scrapy.Spider):
    name = 'pixivsearchspider'
    allowed_domains = ['pixiv.net']
    tag = input('检索作品： ')
    bookmark = int(input('输入最小收藏数： '))
    cookie = input('输入你的cookie： ')
    headers = {
        'authority': 'pixon.ads-pixiv.net',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        'sec-fetch-dest': 'iframe',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'navigate',
        'referer': 'https://www.pixiv.net/',
        'accept-language': 'zh-CN,zh;q=0.9,ja;q=0.8',
        'cookie': cookie,
}
    page = 1
    base_url = 'https://www.pixiv.net/ajax/search/artworks/{}?word={}&order=date_d&mode=all&p={}&s_mode=s_tag&type=all&lang=ja'
    start_urls = ['https://www.pixiv.net/ajax/search/artworks/{}?word={}&order=date_d&mode=all&p={}&s_mode=s_tag&type=all&lang=ja'.format(
        tag, tag, page)]

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0], callback=self.parse, headers=self.headers)

    def parse(self, response):
        html = response.body.decode('utf-8')
        illust_ids = re.findall('"illustId":"(.*?)"', html)
        for illust_id in illust_ids:
            artwork_url = 'https://www.pixiv.net/artworks/{}'.format(illust_id)
            yield scrapy.Request(artwork_url, callback=self.get_img_url, headers=self.headers)

        self.page += 1
        yield scrapy.Request(url=self.base_url.format(self.tag, self.tag, self.page), callback=self.parse, headers=self.headers)

    def get_img_url(self, response):
        artwork_html = response.body.decode('utf-8')
        bookmark_count = re.findall(
            '"width":.*?,"height":.*?,"pageCount":.*?,"bookmarkCount":(.*?),"likeCount":.*?,"commentCount":.*?',
            artwork_html)
        if int(bookmark_count[0]) >= self.bookmark:
            img_url = re.findall('{"mini":".*?","thumb":".*?","small":".*?","regular":"(.*?)","original":".*?"}',
                                 artwork_html)
            img_url = img_url[0]
            item = PixivsearchItem()
            item['img_url'] = img_url
            item['tag'] = self.tag
            yield item


