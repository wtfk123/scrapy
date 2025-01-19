import scrapy 
from scrapy.loader.processors import TakeFirst, Identity, Compose, Join
class MovieItem(scrapy.Item):
    _id=scrapy.Field()
    name = scrapy.Field()#名字
    information = scrapy.Field()#文章内容
    date = scrapy.Field()#日期
    editor = scrapy.Field()#作者
    editor_introduction = scrapy.Field()#作者
    like=scrapy.Field()
    crawling_time=scrapy.Field()
    website_url=scrapy.Field()
    froms=scrapy.Field()#来源媒体
    image_urls=scrapy.Field()
    image_urls_split=scrapy.Field()#图片url
    image_data=scrapy.Field()
    video_urls=scrapy.Field()
    video_data=scrapy.Field()
    video_urls_split=scrapy.Field()#视频URL
    audio_urls=scrapy.Field()
    audio_urls_split=scrapy.Field()
    audio_data=scrapy.Field()
    comment_date=scrapy.Field()
    comment=scrapy.Field()
    comment_name=scrapy.Field()
    comment_number=scrapy.Field()
    formatted_date=scrapy.Field()
    ip=scrapy.Field()#ip地址
    url_from = scrapy.Field()#网站来源