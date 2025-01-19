from urllib.parse import urljoin,urlparse
from bs4 import BeautifulSoup
import requests
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, Identity, Compose,Join
from bson import binary
class MovieItemLoader(ItemLoader):
    default_output_processor = TakeFirst()
    information_out = Join()
    name_out=Compose(TakeFirst(), str.strip)
    editor_out = Compose(TakeFirst(), str.strip)
    editor_introduction_out = Compose(TakeFirst(), str.strip)
    froms_out = Compose(TakeFirst(), str.strip)
    date_out=Join()
    like_out=Join()
    website_url_out=Compose(TakeFirst(), str.strip)
    crawling_time_out=Compose(TakeFirst(), str.strip)
    image_urls_out = Join()
    image_data_out=Join()
    image_urls_split_out=Join()
    formatted_date_out=Join()
    video_urls_out=Join()
    video_data_out=Join()
    video_urls_split_out=Join()
    audio_urls_out=Join()
    audio_urls_split_out=Join()
    audio_data_out=Join()
    ip_out=Join()
    comment_date=Compose(TakeFirst(), str.strip)
    comment=Join
    comment_name=Compose(TakeFirst(), str.strip)
    comment_number=Compose(TakeFirst(), str.strip)
    url_from_out = Join()

