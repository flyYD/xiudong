# -*- coding: utf-8 -*- 
# @File : artistspider.py

import scrapy
from xiudong.items import artistItem


class artistSpider(scrapy.Spider):
    name = "artist_spider"
    allowed_domains = ["www.showstart.com"]
    # 每个爬虫指定管道
    custom_settings = {
        'ITEM_PIPELINES': {'xiudong.pipelines.artistPipeline': 300}
    }

    offset = 1
    url = "https://www.showstart.com/artist/list?pageNo="

    start_urls = [url + str(offset)]
    artist_page_list_temp = []

    def parse(self, response):
        self.get_artist_lists(response)
        # 遍历所有详情页url
        for artist_item in self.artist_page_list_temp:
            print(str(artist_item))
            yield scrapy.Request(str(artist_item), callback=self.artist_parse)
        # 单条数据测试
        # yield scrapy.Request(str(self.artist_page_list_temp[1]), callback=self.artist_parse)
        self.offset += 1
        if self.offset <= 1198:
            yield scrapy.Request(self.url + str(self.offset), callback=self.parse)

    # 解析音乐人详情页数据
    def artist_parse(self, response):
        # print(response.text)
        item = artistItem()
        item["detail_url"] = response.url
        name_xpath = response.xpath('//div[@class="main"]//div[@class="name"]/text()')
        artist_img_xpath = response.xpath('//div[@class="main"]//div[@class="profile-photo ll"]//img/@original')
        area_style_xpath = response.xpath('//div[@class="main"]//ol[@class="dec"]/li/text()')
        introduce_xpath = response.xpath('//div[@class="main"]//div[@class="detalils-wrap"]//div[@id="tab1"]//p')
        about_img_xpath = response.xpath('//div[@class="main"]//div[@class="detalils-wrap"]//div[@id="tab7"]//li/a/@href')
        music_works_xpath = response.xpath('//*[@id="tab4"]/div/ul/li')
        # print(music_works_xpath.extract())
        # 音乐人名称
        if len(name_xpath) > 0:
            item["name"] = str(name_xpath[0].extract()).replace(" ","")
        # 图片
        if len(artist_img_xpath) > 0:
            item["artist_img"] = artist_img_xpath[0].extract()
        # 地区
        if len(area_style_xpath) > 0:
            item["area"] = str(area_style_xpath[0].extract()).replace(" ","").replace("\t","").replace("\r","").replace("\n","").replace("地区：","")
        # 风格
        if len(area_style_xpath) > 1:
            item["style"] = str(area_style_xpath[1].extract()).replace(" ","").replace("\t","").replace("\r","").replace("\n","").replace("风格：","")
        else:
            item["style"] = ""
        # 简介
        if len(introduce_xpath) > 0:
            # print(type(introduce_xpath.extract()))
            item["introduce"] = str(introduce_xpath.xpath('string(.)')[0].extract()).replace(" ","").replace("\t","").replace("\r","").replace("\n","").replace('<br>','')
        else:
            item["introduce"] = "暂无简介"
        # 相关图片
        item["about_img_list"] = []
        for about_img_item in about_img_xpath:
            item["about_img_list"].append(about_img_item.extract())
        # 作品集
        item["music_works_list"] = []
        for music_item in music_works_xpath:
            music_dict = {}
            music_name = str(music_item.xpath('./span[@class="a-link"]/text()').extract_first()).replace(" ","").replace("\t","").replace("\r","").replace("\n","")
            music_play_url = str(music_item.xpath('div[@class="jp-jplayer"]/@playsrc').extract_first()).replace(" ","").replace("\t","").replace("\r","").replace("\n","")
            music_dict["music_name"] = music_name
            music_dict["music_play_url"] = music_play_url
            music_dict["music_player"] = item["name"]
            item["music_works_list"].append(music_dict)
        yield item

    # 解析音乐人列表，获取音乐人详情页url
    def get_artist_lists(self, response):
        self.artist_page_list_temp = []
        links = response.xpath('//div[@class="main auto-width"]//ul//li')
        for linkItem in links:
            link_href_item = linkItem.xpath('.//a[@class="g-name a-link"]/@href').extract_first()
            if not (link_href_item is None):
                self.artist_page_list_temp.append(link_href_item)
