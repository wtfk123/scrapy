# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from datetime import datetime
from urllib.parse import urlparse
from bson import Binary
from itemadapter import ItemAdapter
import pymongo
import requests
from itemadapter import ItemAdapter
import os

import hashlib
from os.path import realpath, dirname, join
from pymongo import MongoClient
from gridfs import GridFS
from .utils import get_config
import argparse 
from bson import binary
#from .pyaud import download_video
parser = argparse.ArgumentParser(description='Universal Spider')
parser.add_argument('name', help='name of spider to run')
args = parser.parse_args()
name = args.name
config = get_config(name)

ip = config.get('type')
url_from = config.get('url_from')
db_name=config.get('dbase')
collection=config.get('collection')
# 提取数据库名字
#data=config.get('dbase')
#db_name = data

class Scrapyuniversaldemo4Pipeline(object):
    def open_spider(self, spider):
        self.client = MongoClient("mongodb://127.0.0.1:27017")
        self.db = self.client[db_name]
        self.collection = self.db[collection]
        self.fs = GridFS(self.db, collection=collection)

    def process_item(self, item, spider):
        query = {'name': item['name']}
        existing_record = self.collection.find_one(query)
        item['ip'] = ip
        item['url_from'] = url_from
        if not existing_record:
            # 处理图片
            if 'image_urls' in item:
                image_urls = item['image_urls'].split()
                item['image_urls_split'] = image_urls  # 将字符串拆分成URL列表
                processed_urls = []
                for url in image_urls:
                    try:
                        image_data = requests.get(url, timeout=20).content
                        processed_urls.append(Binary(image_data))
                    except requests.exceptions.RequestException as e:
                        print(f"Error downloading image from URL: {url}")
                        print(f"Error details: {str(e)}")
                item['image_data'] = processed_urls

                del item['image_urls']  # 删除image_urls属性

            # 处理视频
            if 'video_urls' in item:
                video_url = item['video_urls']
                item['video_urls_split'] = video_url  # 将视频URL列表存储在新键中
            
                try:
                    video_data = requests.get(video_url, timeout=30).content
                    filename = urlparse(video_url).path.split("/")[-1]
                    video_id = self.fs.put(video_data, filename=filename)
                    item['video_data'] = video_id
                except requests.exceptions.RequestException as e:
                    print(f"Error downloading video from URL: {video_url}")
                    print(f"Error details: {str(e)}")

                del item['video_urls'] 

            #处理音频
            if 'audio_urls' in item:
                audio_urls = item['audio_urls']
                item['audio_urls_split'] = audio_urls  # 将音频URL存储在新键中
                audio_data_list = []
                for audio_url in audio_urls:
                    try:
                        audio_data = requests.get(audio_url, timeout=30).content
                        audio_id = self.fs.put(audio_data, filename="audio.mp3")
                        audio_data_list.append(audio_id)
                    except requests.exceptions.RequestException as e:
                        print(f"Error downloading audio from URL: {audio_url}")
                        print(f"Error details: {str(e)}")
                item['audio_data'] = audio_data_list

                del item['audio_urls']

            self.collection.insert_one(item)
        else:
            print(f"Duplicate found: {item}")

        return item

    def close_spider(self, spider):
        self.client.close()


"""        #try:
with open('data.json', 'r') as file:
    data = json.load(file)
        self.db.update_one({'name': item['name']},
            {'$set': dict(item)},
            upsert=True) 
        #except DuplicateKeyError:
         #   print(f'_id为{item["_id"]},name为 {item["name"]}')
        #else:
                query = {'name': item['name']}
        # 在插入前检查是否已存在相同的记录
        existing_record = self.db.find_one(query)
        item["image_urls"] = binary.Binary(data1)
        if not existing_record:
            
            item = dict(item)
            self.db.insert_one(item) 
        else:
            print(f"Duplicate found: {item}")

        return item"""