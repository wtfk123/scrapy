from scrapy.utils.project import get_project_settings
from scrapyuniversaldemo.utils import get_config
from scrapy.crawler import CrawlerProcess
import argparse
import scrapy
import time


class SpiderRunner:
    def __init__(self, name):
        self.name = name

    def run(self):
        config = get_config(self.name)
        spider = config.get('spider', 'universal')
        project_settings = get_project_settings()
        settings = dict(project_settings.copy())
        settings.update(config.get('settings'))
        process = CrawlerProcess(settings)
        process.crawl(spider, **{'name': self.name})
        process.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Universal Spider')
    parser.add_argument('name', help='name of spider to run')
    args = parser.parse_args()

    name = args.name

    spider_runner = SpiderRunner(name)
    spider_runner.run()
    