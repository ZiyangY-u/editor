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

TIMEOUT = httpx.Timeout(10.0, connect=10.0)
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
skip_urls = {}

# 人民日报
PEOPLE_AID_TYPE = 1
PEOPLE_ARTICLE_REGEX = r'.*people\.com\.cn.*?[a-z0-9]{3,6}-[a-z0-9]{8}\.html'
# 新华社
NEWS_AID_TYPE = 2
NEWS_ARTICLE_REGEX = r'.*[0-9]{8}/[a-z0-9]{32}/c.html'
NEWS_HOME = 'https://www.news.cn/'
# 新京报
BJNEWS_AID_TYPE = 3
BJNEWS_ARTICLE_REGEX = r'.*/detail/[0-9]{16}.html'
BJNEWS_HOME = 'https://www.bjnews.com.cn/'

history_url_json_file = 'c-idiom-urls.json'
skip_url_json_file = 'c-idiom-skip-urls.json'

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
    return urlunparse(cleaned).replace('"', '')

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
        with open(f'{folder_path}/article-{self.word}-.txt', 'w+', encoding='utf8') as f:
            f.write(f'对于成语‘{self.word}’\n')
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
    if 'news.cn' in url:
        return NEWS_AID_TYPE
    if 'bjnews.com.cn' in url:
        return BJNEWS_AID_TYPE
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
    # count result file
    kw = target_file.split('-')[1]
    kw_cnt = 0
    for filename in os.listdir(one_drive_target_path):
        if kw in filename:
            kw_cnt += 1
    target_file = target_file.split('/')[-1].replace(kw, f'{kw}-{kw_cnt+1}')
    shutil.copyfile(fname, f'{one_drive_target_path}\\{target_file}')
    if target.target_cnt == len(target.hit_urls):
        print(f'{kw} complete!')
        target.completed = True

def parse_txt_article(url):
    global targets
    fp = f'{cache_folder}/{u2f(url)}.txt'
    size_bytes = os.path.getsize(fp)
    if size_bytes < 1024:
        del article_urls[url]
        delete_file(fp)
        skip_urls[url] = 1
        return
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

# 新华社
def parse_news_article(content, url):
    doc = pq(content)
    headers = doc('h1')
    headers = [str(p.text()) for p in headers.items() if len(str(p.text()).strip()) != 0]
    paragraphs = doc('p')
    paragraphs = [str(p.text()) for p in paragraphs.items()]
    write_paragraphs(url, headers[0] if len(headers) > 0 else '', paragraphs)

# 新京报
def parse_bjnews_article(content, url):
    pass

def is_article_url(url):
    t = determine_type_by_aid(url)
    if t == PEOPLE_AID_TYPE and re.match(PEOPLE_ARTICLE_REGEX, url):
        return True
    if t == NEWS_AID_TYPE and re.match(NEWS_ARTICLE_REGEX, url):
        return True
    if t == BJNEWS_AID_TYPE and re.match(BJNEWS_ARTICLE_REGEX, url):
        return True
    return False

def parse_article(content, url):
    try:
        recruit_from_content(content)
    except:
        print(f'\nerror in recruit from {url}', end='')
    t = determine_type_by_aid(url)
    if is_article_url(url):
        if t == PEOPLE_AID_TYPE:
            parse_people_article(content, url)
        if t == NEWS_AID_TYPE:
            parse_news_article(content, url)
        if t == BJNEWS_AID_TYPE:
            parse_news_article(content, url)
    article_urls[url] = 1 # marked as searched

def valid_url(url):
    if 'people.com' in url:
        return True
    if 'news.cn' in url:
        return True
    if 'bjnews.com.cn' in url:
        return True
    return False

def recruit_from_content(content):
    doc = pq(content)
    anchors = doc('a')
    for a in anchors:
        if 'href' not in a.attrib:
            continue
        raw_ref = a.attrib['href']
        if 'news.cn' in raw_ref and raw_ref.startswith('//'):
            raw_ref = 'https:' + raw_ref
        if re.match(NEWS_ARTICLE_REGEX, raw_ref) and raw_ref.startswith('/') and 'https:' not in raw_ref:
            raw_ref = NEWS_HOME + raw_ref
        ref = remove_url_params(raw_ref)
        if valid_url(ref) and ref not in article_urls:
            article_urls[ref] = 0 # recruit url

def recruit_from_url(url):
    global article_urls
    before = len(article_urls)
    try:
        response = requests.get(url, timeout=15.0)
        recruit_from_content(response.content)
    except:
        print(f'error in recruiting from {url}')
    recruited = len(article_urls) - before
    print(f'recruit {recruited} from {url}')

def recruit_from_home():
    recruit_targets = [
            'http://www.people.com.cn/',
            'https://www.news.cn/',
            'https://www.bjnews.com.cn/',
            'http://hb.people.com.cn/',
            'https://www.news.cn/comments/index.html',
            'https://www.bjnews.com.cn/zhengshi',
            'https://www.bjnews.com.cn/hao',
            'https://www.bjnews.com.cn/depth',
            'https://www.bjnews.com.cn/gongyi',
            'https://www.bjnews.com.cn/diyikandian',
            # 'https://www.bjnews.com.cn/news',
            # 'https://www.bjnews.com.cn/beijing',
            # 'https://www.bjnews.com.cn/guoji',
            # 'https://www.bjnews.com.cn/zhengshi',
            # 'https://www.bjnews.com.cn/point',
            # 'https://www.bjnews.com.cn/financial',
            # 'https://www.bjnews.com.cn/industrial',
            # 'https://www.bjnews.com.cn/entertainment',
            # 'https://www.bjnews.com.cn/culture',
            # 'https://www.bjnews.com.cn/sports',
            # 'https://www.bjnews.com.cn/car',
            # 'https://www.bjnews.com.cn/estate',
            # 'https://www.bjnews.com.cn/education',
            # 'https://www.bjnews.com.cn/photo',
            # 'https://www.bjnews.com.cn/technology',
            # 'https://www.bjnews.com.cn/thinktank',
            # 'https://www.bjnews.com.cn/country',
            ]
    rts = random.sample(recruit_targets, 5)
    for t in rts:
        recruit_from_url(t)


def load_history_and_summary():
    if file_accessable(history_url_json_file): # get init article ids from last history
        with open(history_url_json_file, 'r', encoding='utf8') as fp:
            content = json.load(fp)
            _tmp_fn = set()
            for filename in os.listdir(cache_folder):
                _tmp_fn.add(filename)
            for url, _ in content.items():
                article_urls[url] = 0
                if u2f(url) + '.txt' in _tmp_fn:
                    cached_article_urls.add(url)
        print(f'load urls from history: {len(article_urls)}')
        print(f'load cached urls from history: {len(cached_article_urls)}')
    if file_accessable(skip_url_json_file): # skip list
        with open(skip_url_json_file, 'r', encoding='utf8') as fp:
            content = json.load(fp)
            for k, _ in content.items():
                skip_urls[k] = 1

def save_history():
    with open(history_url_json_file, 'w+', encoding='utf8') as fp: # save article_ids
        json.dump(article_urls, fp)
        print(f'{len(article_urls)} urls saved')
    with open(skip_url_json_file, 'w+', encoding='utf8') as fp: # save skip_urls
        json.dump(skip_urls, fp)

def unsearched(url):
    if url not in article_urls:
        return True
    if article_urls[url] == 0:
        return True
    return False

def sampling_urls():
    uncached = [k for k, v in article_urls.items() if v == 0 and k not in cached_article_urls and k not in skip_urls]
    urls_uncache = random.sample(uncached, THREADS) if len(uncached) > THREADS else []

    urls_cached = [k for k in cached_article_urls if k not in skip_urls]
    urls_cached = random.sample(urls_cached, MAX_THREADS) if len(urls_cached) > MAX_THREADS else []

    urls_expand = [k for k, v in article_urls.items() if v == 0 and len(k) < 50]
    urls_expand = random.sample(urls_expand, THREADS) if len(urls_expand) > THREADS else []

    urls = [url for url in (urls_uncache + urls_cached + urls_expand) if unsearched(url)]
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

def delete_file(file_path):
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)  # 删除文件或符号链接
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)  # 删除子文件夹（可选）
    except Exception as e:
        print(f"删除 {file_path} 失败: {e}")

def delete_tmp_articles():
    global folder_path
    for filename in os.listdir(folder_path):
        if not filename.startswith('article-'):
            continue
        file_path = os.path.join(folder_path, filename)
        delete_file(file_path)

def crawl(targets):
    recruit_from_home()

    print('start')
    max_loop = 200
    loop_cnt = 0
    while not all(t.completed for t in targets) and urls_info(0) > THREADS and not file_accessable('./stop.txt') and loop_cnt < max_loop:
        if file_accessable(ONE_DRIVE_PATH + '\\stop.txt'):
            break
        loop_cnt += 1
        urls = sampling_urls()
        info = f'{loop_cnt}th run at {datetime.now().strftime("%m/%d/%Y %H:%M:%S")}'
        info += f' {len([k for k, v in article_urls.items() if v == 1])} searched'
        print(f'{info}\n', end='')
        done_urls = asyncio.run(launch(get_content_and_parse, urls))
        for url in done_urls:
            article_urls[url] = 1

def get_targets_from_list():
    everyday_idioms_cnt = 10
    list_path = ONE_DRIVE_PATH + '\\c-idioms.txt'
    if not file_accessable(list_path):
        print(f'list not accessable {list_path}')
        return []
    _targets1 = []
    if file_accessable(f'{ONE_DRIVE_PATH}\\c-targets.txt'):
        with open(ONE_DRIVE_PATH + '\\c-targets.txt', 'r', encoding='utf8') as f:
            content = f.read().splitlines()
            _targets1 = [Target(word=w) for w in content]

    with open(list_path, 'r', encoding='utf8') as f:
        idiom_list = f.read().splitlines()
        random.seed(datetime.now().strftime("%Y%m%d"))
        idioms = random.sample(idiom_list, everyday_idioms_cnt)
        _targets = [Target(word=w) for w in idioms]
        return [t for t in (_targets + _targets1)]


if __name__ == '__main__':
    # delete_tmp_articles()
    while True:
        targets = get_targets_from_list()

        load_history_and_summary()
        crawl(targets)
        save_history()
        time.sleep(60 * 5) # 5 minutes
