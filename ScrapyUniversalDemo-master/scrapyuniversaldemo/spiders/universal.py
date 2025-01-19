from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..utils import get_config
from .. import items, loaders
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import datetime
class UniversalSpider(CrawlSpider):
    name = 'universal'

    def __init__(self, name, *args, **kwargs):
        super(UniversalSpider, self).__init__(*args, **kwargs)
        config = get_config(name)
        self.config = config
        self.start_urls = config.get('start_urls')
        self.allowed_domains = config.get('allowed_domains')
        self.model=config.get('model')
        self.video = config.get('video', None)
        self.video_src = config.get('video_src', None)
        self.button = config.get('button', None)
        self.audio = config.get('audio', None)
        self.audio_src = config.get('audio_src', None)
        filename = 'start_urls.json'
        with open(filename, 'a') as file:
             json.dump(self.start_urls, file, indent=4)
        rules = []
        for rule_kwargs in config.get('rules'):
            link_extractor = LinkExtractor(**rule_kwargs.get('link_extractor'))
            rule_kwargs['link_extractor'] = link_extractor
            rule = Rule(**rule_kwargs)
            rules.append(rule)
        self.rules = rules
        super(UniversalSpider, self).__init__(*args, **kwargs)
    def is_absolute_url(self,url):
        parsed_url = urlparse(url)
        return bool(parsed_url.netloc)
    def convert_to_absolute_url(self,base_url, url):
        if self.is_absolute_url(url):
            return url
        else:
            return urljoin(base_url, url)
    def get_absolute_image_urls(self,url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        image_urls = []
        # 查找所有的图片标签
        img_tags = soup.find_all('img')
        for img_tag in img_tags:
            # 获取图片标签的src属性
            src = img_tag.get('src')
            
            # 构建绝对路径
            absolute_url = self.convert_to_absolute_url(url, src)
            
            # 将绝对路径添加到列表中
            image_urls.append(absolute_url)
            
        return image_urls

    def execute_another_function(self, url):
        options = Options()
        #options.add_argument('--headless')
        options.add_argument('--ignore-certificate-errors')
        options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
        driver = webdriver.Chrome(options=options)

        driver.get(url)
        wait = WebDriverWait(driver, 10)
        try:
            # Find and click the Agree and Close button
            agree_button = wait.until(EC.presence_of_element_located((By.ID, self.button)))
            agree_button.click()

            # Find video elements
            video_elements = driver.find_elements(By.TAG_NAME, self.video)
            video_urls = [video.get_attribute(self.video_src) for video in video_elements]

            # Find audio
            audio_elements = driver.find_elements(By.TAG_NAME, self.audio)
            audio_urls = [audio.get_attribute(self.audio_src) for audio in audio_elements]

            driver.quit()  # 在正常处理后退出浏览器驱动

            # 返回获取的视频URL和音频URL
            yield {'video_urls': video_urls, 'audio_urls': audio_urls}
        except Exception as e:
            print(f"Error occurred while processing URL: {url}")
            print(f"Error details: {str(e)}")
            driver.quit()  # 在异常情况下也要确保退出浏览器驱动
            yield {'video_urls': [], 'audio_urls': []}  # 返回默认的空列表作为视频URL和音频URL
    def parse_detail(self, response):
        # 获取网页的URL
        url = response.url
        # 第一次爬取,爬取图片URL和文本
        image_urls = self.get_absolute_image_urls(url)
        item = self.config.get('item')
        if item:
            cls = getattr(items, item.get('class'))()
            loader = getattr(loaders, item.get('loader'))(cls, response=response)
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # last_modified = response.headers.get('last-modified')
            # last_modified_dt = datetime(last_modified, '%a, %d %b %Y %H:%M:%S GMT')
            # formatted_date = last_modified.strftime(last_modified, '%Y-%m-%d %H:%M:%S')
            loader.add_value('crawling_time', current_time)
            loader.add_value('website_url', url)
            if image_urls:
                # 添加图片URL
                loader.add_value('image_urls', image_urls)
            
            # if formatted_date:
            #    loader.add_value('last_modified', formatted_date)

    
            for key, value in item.get('attrs').items():
                for extractor in value:
                    if extractor.get('method') == 'xpath':
                        loader.add_xpath(key, extractor.get('arg'), **{'re': extractor.get('re')})
                    if extractor.get('method') == 'css':
                        loader.add_css(key, extractor.get('arg'), **{'re': extractor.get('re')})
                    if extractor.get('method') == 'value':
                        loader.add_value(key, extractor.get('args'), **{'re': extractor.get('re')})        
            # 返回 Item 对象
            yield loader.load_item()
        # 第二次爬取,爬取音频和视频数据
        if self.model:
            video_urls,audio_urls= self.execute_another_function(url)
            if item:
                cls = getattr(items, item.get('class'))()
                loader = getattr(loaders, item.get('loader'))(cls, response=response)
                loader.add_value('video_urls', video_urls)
                loader.add_value('audio_urls', audio_urls)
            yield loader.load_item()

"""class UniversalSpider(CrawlSpider):
    name = 'universal'

    def __init__(self, name, *args, **kwargs):
        super(UniversalSpider, self).__init__(*args, **kwargs)
        config = get_config(name)
        self.config = config
        self.start_urls = config.get('start_urls')
        self.allowed_domains = config.get('allowed_domains')

        # Set attributes from config
        self.img = config.get('img')
        self.img_src = config.get('img_src')
        self.video = config.get('video')
        self.video_src = config.get('video_src')
        self.button = config.get('button')
        self.audio=config.get('audio')
        self.audio_src=config.get('audio_src')
        # Write start_urls to JSON file
        with open('start_urls.json', 'w') as file:
            json.dump(self.start_urls, file, indent=4)

        rules = []
        for rule_kwargs in config.get('rules'):
            link_extractor = LinkExtractor(**rule_kwargs.get('link_extractor'))
            rule_kwargs['link_extractor'] = link_extractor
            rule = Rule(**rule_kwargs)
            rules.append(rule)
        self.rules = rules
        super(UniversalSpider, self).__init__(*args, **kwargs)
    def agree_to_continue(self, url):
        options = Options()
        #options.add_argument('--headless')
        options.add_argument('--ignore-certificate-errors')
        options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
        driver = webdriver.Chrome(options=options)

        driver.get(url)
        wait = WebDriverWait(driver, 10)
        try:
            # Find and click the Agree and Close button
            agree_button = wait.until(EC.presence_of_element_located((By.ID, self.button)))
            agree_button.click()

            # Find video elements
            video_elements = driver.find_elements(By.TAG_NAME, self.video)
            video_urls = [video.get_attribute(self.video_src) for video in video_elements]

            # Find image elements
            image_elements = driver.find_elements(By.TAG_NAME, self.img)
            base_url = driver.current_url
            image_urls = []

            for img in image_elements:
                img_src = img.get_attribute(self.img_src)
                parsed_url = urlparse(img_src)

                if parsed_url.scheme and parsed_url.netloc:
                    # Absolute URL
                    image_urls.append(img_src)
                else:
                    # Relative URL, convert it to absolute URL
                    absolute_url = urljoin(base_url, img_src)
                    image_urls.append(absolute_url)
                    
            #find audio
            audio_elements = driver.find_elements(By.TAG_NAME, 'audio')
            audio_urls = [audio.get_attribute('src') for audio in audio_elements]


            driver.quit()  # 在正常处理后退出浏览器驱动

            return video_urls, image_urls,audio_urls  # 返回获取的视频URL和图片URL
        except Exception as e:
            print(f"Error occurred while processing URL: {url}")
            print(f"Error details: {str(e)}")
            driver.quit()  # 在异常情况下也要确保退出浏览器驱动
            return [], [], [] # 返回默认的空列表作为视频URL和图片URL

    def parse_detail(self, response):
        url = response.url
        video_urls, image_urls, audio_urls = self.agree_to_continue(url)

        item = self.config.get('item')
        if item:
            cls = getattr(items, item.get('class'))()
            loader = getattr(loaders, item.get('loader'))(cls, response=response)
            # Add crawling time and website URL
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            loader.add_value('crawling_time', current_time)
            loader.add_value('website_url', url)
            if image_urls:
                loader.add_value('image_urls', image_urls)
            if video_urls:
                loader.add_value('video_urls', video_urls)
            if audio_urls:
                loader.add_value('audio_urls', audio_urls)
            for key, value in item.get('attrs').items():
                for extractor in value:
                    if extractor.get('method') == 'xpath':
                        loader.add_xpath(key, extractor.get('arg'), **{'re': extractor.get('re')})
                    if extractor.get('method') == 'css':
                        loader.add_css(key, extractor.get('arg'), **{'re': extractor.get('re')})
                    if extractor.get('method') == 'value':
                        loader.add_value(key, extractor.get('args'), **{'re': extractor.get('re')})

        yield loader.load_item()"""

"""from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..utils import get_config
from .. import items, loaders
import json
import requests
from datetime import datetime
from bson import binary
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
class UniversalSpider(CrawlSpider):
    name = 'universal'

    def __init__(self, name, *args, **kwargs):
        super(UniversalSpider, self).__init__(*args, **kwargs)
        config = get_config(name)
        self.config = config
        self.start_urls = config.get('start_urls')
        self.allowed_domains = config.get('allowed_domains')

        # Set attributes from config
        self.img = config.get('img')
        self.img_src = config.get('img_src')
        self.video = config.get('video')
        self.video_src = config.get('video_src')
        self.button = config.get('button')

        # Write start_urls to JSON file
        with open('start_urls.json', 'w') as file:
            json.dump(self.start_urls, file, indent=4)

        rules = []
        for rule_kwargs in config.get('rules'):
            link_extractor = LinkExtractor(**rule_kwargs.get('link_extractor'))
            rule_kwargs['link_extractor'] = link_extractor
            rule = Rule(**rule_kwargs)
            rules.append(rule)
        self.rules = rules

    @staticmethod
    def convert_to_absolute_url(base_url, url):
        if urlparse(url).netloc:
            return url
        else:
            return urljoin(base_url, url)

    def get_absolute_image_urls(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        image_urls = []

        # Find all image tags
        img_tags = soup.find_all(self.img)
        for img_tag in img_tags:
            # Get the src attribute of each image tag
            src = img_tag.get(self.img_src)
            absolute_url = self.convert_to_absolute_url(url, src)
            image_urls.append(absolute_url)
            
        return image_urls

    def agree_to_continue(self, url, user_agent):
        options = Options()
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument('--headless')
        options.add_argument('--ignore-certificate-errors')
        options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
        driver = webdriver.Chrome(options=options)

        driver.get(url)
        wait = WebDriverWait(driver, 10)

        # Find and click the Agree and Close button
        agree_button = wait.until(EC.presence_of_element_located((By.ID, self.button)))
        agree_button.click()

        # Find video elements
        video_elements = driver.find_elements(By.TAG_NAME, self.video)
        video_urls = []
        for video in video_elements:
            video_url = video.get_attribute(self.video_src)
            video_urls.append(video_url)

        driver.quit()
        return video_urls

    def parse_detail(self, response):
        url = response.url
        image_urls = self.get_absolute_image_urls(url)
        video_urls = self.agree_to_continue(url, user_agent)

        item = self.config.get('item')
        if item:
            cls = getattr(items, item.get('class'))()
            loader = getattr(loaders, item.get('loader'))(cls, response=response)
            if image_urls:
                loader.add_value('image_urls', image_urls)
            if video_urls:
                loader.add_value('video_url', video_urls)
            for key, value in item.get('attrs').items():
                for extractor in value:
                    if extractor.get('method') == 'xpath':
                        loader.add_xpath(key, extractor.get('arg'), **{'re': extractor.get('re')})
                    if extractor.get('method') == 'css':
                        loader.add_css(key, extractor.get('arg'), **{'re': extractor.get('re')})
                    if extractor.get('method') == 'value':
                        loader.add_value(key, extractor.get('args'), **{'re': extractor.get('re')})

        yield loader.load_item()
"""
"""from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..utils import get_config
from .. import items, loaders
import json
import requests
from datetime import datetime
from ..items import MovieItem
import pyaudio
#from ..pyaud import download_video

from bson import binary
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
    def is_absolute_url(url):
        parsed_url = urlparse(url)
        return bool(parsed_url.netloc)

    def convert_to_absolute_url(base_url, url):
        if self.is_absolute_url(url):
            return url
        else:
            return urljoin(base_url, url)

    def get_absolute_image_urls(url):

        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        image_urls = []

        # 查找所有的图片标签
        img_tags = soup.find_all('img')
        for img_tag in img_tags:
            # 获取图片标签的src属性
            src = img_tag.get('src')
            
            # 构建绝对路径
            absolute_url = self.convert_to_absolute_url(url, src)
            
            # 将绝对路径添加到列表中
            image_urls.append(absolute_url)
            
        return image_urls
class UniversalSpider(CrawlSpider):
    name = 'universal'
    
    def __init__(self, name, *args, **kwargs):
        config = get_config(name)
        self.config = config
        self.start_urls = config.get('start_urls')
        self.allowed_domains = config.get('allowed_domains')
        filename = 'start_urls.json'
        with open(filename, 'a') as file:
             json.dump(self.start_urls, file, indent=4)
        rules = []
        for rule_kwargs in config.get('rules'):
            link_extractor = LinkExtractor(**rule_kwargs.get('link_extractor'))
            rule_kwargs['link_extractor'] = link_extractor
            rule = Rule(**rule_kwargs)
            rules.append(rule)
        self.rules = rules
        
        super(UniversalSpider, self).__init__(*args, **kwargs)

    def parse_detail(self, response):
        # 获取网页的URL
        url = response.url
        
        # 获取网页中所有图片的绝对路径
        image_urls = get_absolute_image_urls(url)
        #video_urls=self.agree_to_continue(url, user_agent)
        item = self.config.get('item')
        if item:
            cls = getattr(items, item.get('class'))()
            loader = getattr(loaders, item.get('loader'))(cls, response=response)
            if image_urls:
            # 添加图片URL
                loader.add_value('image_urls', image_urls)
            #if video_urls:
               #loader.add_value('video_url', video_urls)
            for key, value in item.get('attrs').items():
                for extractor in value:
                    if extractor.get('method') == 'xpath':
                        loader.add_xpath(key, extractor.get('arg'), **{'re': extractor.get('re')})
                    if extractor.get('method') == 'css':
                        loader.add_css(key, extractor.get('arg'), **{'re': extractor.get('re')})
                    if extractor.get('method') == 'value':
                        loader.add_value(key, extractor.get('args'), **{'re': extractor.get('re')})
            
        yield loader.load_item()

 

   def parse(self, response):
        # 发送HTTP HEAD请求获取Last-Modified标头
        headers = requests.head(response.url).headers
        last_modified_header = headers.get('Last-Modified')

        # 将Last-Modified转换为datetime对象
        last_modified = datetime.strptime(last_modified_header, "%a, %d %b %Y %H:%M:%S %Z") if last_modified_header else None

        # 比较Last-Modified和上次保存的Last-Modified
        if last_modified and last_modified != self.last_modified:
            # 更新Last-Modified
            self.last_modified = last_modified

            # 执行相应的爬取操作
            yield from super().parse_detail(response)"""

