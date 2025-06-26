#!/usr/bin/python3.8

import requests
import unicodedata
import zipfile
import asyncio
import httpx
import re
import json
import time
import os
import shutil
import random
import itertools
import aiofiles
import logging
from os import access, R_OK
from os.path import isfile
from pyquery import PyQuery as pq
from datetime import datetime
from functools import wraps
from urllib.parse import urlparse, urlunparse

TIMEOUT = httpx.Timeout(5.0, connect=5.0)
ONE_DRIVE_PATH = 'C:\\Users\\fvdi0046\\OneDrive2\\OneDrive\\articles'
MAX_SLEEP_TIME = 600
# logging.basicConfig(filename=ONE_DRIVE_PATH + '\\crawl_log.log',
#                     filemode='a',
#                     format='%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s',
#                     datefmt='%Y-%m-%d %H:%M:%S',
#                     encoding='utf8',
#                     level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.CRITICAL) # not let httpx logging

THREADS = 20
MAX_THREADS = 100
TARGET_CNT = 5 # default target cnt

article_urls = {}
cached_article_urls = set()

# 人民日报
PEOPLE_AID_TYPE = 1
people_article_regex = r'.*people\.com\.cn.*?[a-z0-9]{3,6}-[a-z0-9]{8}\.html'

history_url_json_file = 'c-idiom-urls.json'

folder_path = './articles'
cache_folder = './c-cache'

received_bytes = 0
cache_hit_cnt = 0
tm1 = time.perf_counter()

targets = []

def file_accessable(path):
    if isfile(path) and access(path, R_OK):
        return True
    return False

def remove_url_params(url):
    parsed = urlparse(url)
    # 保留除查询参数外的所有部分
    cleaned = parsed._replace(query=None)
    return urlunparse(cleaned)

async def launch(async_fun, params):
    aids = await asyncio.gather(*map(async_fun, params))
    return aids

class Target:
    def __init__(self, word:str, target_cnt=TARGET_CNT):
        self.word = word
        self.hit_urls = set()
        self.target_cnt = target_cnt
        self.completed = False
        print(f'init target: {self.word}')
        # send explain question to auto-ai
        with open(f'{folder_path}/article-{self.word}.txt', 'w+', encoding='utf8') as f:
            f.write('对于成语‘{self.word}’\n')
            f.write('1.请你标注它的拼音\n')
            f.write('2.解释它的意思并说明适用场景\n')
            f.write('3.说明它的出处\n')

    def get_kw(self):
        return self.word

    def hit(self, paragraph):
        if self.word in paragraph:
            return True

def u2f(url):
    return url.replace('https://', '').replace('http://', '').replace('/', '•')

def urls_info(flg): # 1 searched; 0 remain
    global article_urls
    return len(([k for k, v in article_urls.items() if v == flg]))

def determine_type_by_aid(url):
    if 'people.com' in url:
        return PEOPLE_AID_TYPE
    return PEOPLE_AID_TYPE

def process_hit(target, url, header, paragraph_contents):
    kw = target.get_kw()
    print(f'hit: {kw}')
    fname = f'./{folder_path}/article-{target.get_kw()}-{u2f(url)}.md'
    with open(fname, 'w+', encoding='utf8') as f:
        f.write('### ' + header + '\n')
        for _, p in enumerate(paragraph_contents, start=1):
            p2w = p.replace(kw, f'**{kw}**') if kw in p else p
            f.write(p2w + '\n\n')
    target.hit_urls.add(url)
    # copy result to OneDrive
    one_drive_target_path = ONE_DRIVE_PATH + '\\' + datetime.now().strftime("%Y%m%d")
    if not os.path.exists(one_drive_target_path):
        os.makedirs(one_drive_target_path)
    target_file = fname.split('/')[-1]
    shutil.copyfile(fname, f'{one_drive_target_path}\\{target_file}')
    if target.target_cnt == len(target.hit_urls):
        print(f'{kw} complete!')
        target.completed = True

def parse_txt_article(url):
    global targets
    fp = f'{cache_folder}/{u2f(url)}.txt'
    a_content = []
    with open(fp, 'r', encoding='utf8') as f:
        a_content = [line.strip() for line in f]
    for target in targets:
        if target.completed or url in target.hit_urls:
            continue
        hit_flag = False
        for _, p in enumerate(a_content, start=1):
            if target.hit(p):
                hit_flag = True
        if hit_flag and url not in target.hit_urls:
            process_hit(target, url, a_content[0], a_content[1:])
    article_urls[url] = 1 # marked as searched

def write_paragraphs(url:str, header:str, paragraphs:list):
    fp = f'{cache_folder}/{u2f(url)}.txt'
    with open(fp, 'w+', encoding='utf8') as f:
        f.write(header + '\n\n')
        for _, p in enumerate((p.strip() for p in paragraphs if p.strip() != ''), start=1):
            f.write(p + '\n')
    parse_txt_article(url)

# 人民日报
def parse_people_article(content, url):
    doc = pq(content)
    headers = doc('h1')
    headers = [str(p.text()) for p in headers.items() if len(str(p.text()).strip()) != 0]
    paragraphs = doc('p')
    paragraphs = [str(p.text()) for p in paragraphs.items()]
    write_paragraphs(url, headers[0] if len(headers) > 0 else '', paragraphs)

def is_article_url(url):
    if 'people.com' in url and re.match(people_article_regex, url):
        return True
    return False

def parse_article(content, url):
    try:
        recruit_from_content(content)
    except:
        print(f'error in recruit from {url}')
    type = determine_type_by_aid(url)
    if is_article_url(url):
        if type == PEOPLE_AID_TYPE:
            parse_people_article(content, url)
    article_urls[url] = 1 # marked as searched

def valid_url(url):
    if 'people.com' in url:
        return True
    return False

def recruit_from_content(content):
    doc = pq(content)
    anchors = doc('a')
    for a in anchors:
        if 'href' not in a.attrib:
            continue
        ref = remove_url_params(a.attrib['href'])
        if valid_url(ref):
            article_urls[ref] = 0 # recruit url

def recruit_from_url(url):
    global article_urls
    before = len(article_urls)
    response = requests.get(url, timeout=10.0)
    recruit_from_content(response.content)
    recruited = len(article_urls) - before
    print(f'recruit {recruited} from {url}')

def recruit_from_home():
    try:
        recruit_from_url('http://www.people.com.cn/')
        recruit_from_url('http://hb.people.com.cn/')
    except:
        pass

def load_history_and_summary():
    if file_accessable(history_url_json_file): # get init article ids from last history
        with open(history_url_json_file, 'r', encoding='utf8') as fp:
            content = json.load(fp)
            _tmp_fn = set()
            for filename in os.listdir(cache_folder):
                _tmp_fn.add(filename)
            for url, _ in content.items():
                article_urls[url] = 0
                if u2f(url) in _tmp_fn:
                    cached_article_urls.add(url)
        print(f'load urls from history: {len(article_urls)}')

def save_history():
    with open(history_url_json_file, 'w+', encoding='utf8') as fp: # save article_ids
        json.dump(article_urls, fp)

def unsearched(url):
    if url not in article_urls:
        return True
    if article_urls[url] == 0:
        return True
    return False

def sampling_urls():
    uncached = [k for k, v in article_urls.items() if v == 0 and k not in cached_article_urls]
    urls1 = random.sample(uncached, THREADS) if len(uncached) > THREADS else []
    urls_cached = random.sample([k for k in cached_article_urls], MAX_THREADS) if len(cached_article_urls) > MAX_THREADS else []
    urls = [url for url in (urls1 + urls_cached) if unsearched(url)]
    return urls

async def get_content_and_parse(url):
    content = ''
    path = f'{cache_folder}/{u2f(url)}.html'
    if file_accessable(path):
        parse_txt_article(url)
    else:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            try:
                resp = await client.get(url=url)
                content = resp.content.decode('utf8')
            except:
                logging.info(f'error in request: {url}')
                return url
        parse_article(content, url)
    return url


def crawl(targets, delete_tmp=True):
    recruit_from_home()

    print('start')
    while not all(t.completed for t in targets) and urls_info(0) > THREADS and not file_accessable('./stop.txt'):
        urls = sampling_urls()
        done_urls = asyncio.run(launch(get_content_and_parse, urls))
        for url in done_urls:
            article_urls[url] = 1

def get_targets_from_list():
    everyday_idioms_cnt = 10
    list_path = ONE_DRIVE_PATH + '\\c-idioms.txt'
    if not file_accessable(list_path):
        print(f'list not accessable {list_path}')
        return
    with open(list_path, 'r', encoding='utf8') as f:
        idiom_list = f.read().splitlines()
        idioms = random.sample(idiom_list, everyday_idioms_cnt)
        _targets = [Target(word=w) for w in idioms]
        return _targets




if __name__ == '__main__':
    targets = get_targets_from_list()

    load_history_and_summary()
    crawl(targets)
    save_history()

    # test_url = 'opinion.people.com.cn/n1/2025/0529/c1003-40490150.html'
    # resp = requests.get('http://' + test_url, timeout=10)
    # print(resp.status_code)
    # parse_people_article(resp.content.decode('utf8'), test_url)

