#!/usr/bin/python3.8

import requests
import requests
import zipfile
import asyncio
import httpx
import re
import json
import time
import os
import shutil
import random
import aiofiles
from os import access, R_OK
from os.path import isfile
from pyquery import PyQuery as pq
from datetime import datetime

TIMEOUT = httpx.Timeout(360.0, connect=360.0)
HOME_URL = 'https://www.bbc.com/'
THREADS = 5
TARGET_CNT = 3

article_ids = {}
cached_article_ids = set()
targets = []

folder_path = './en-articles'
cache_folder = './en-cache'
cache_hit_cnt = 0
received_bytes = 0

tm1 = time.perf_counter()

def gaid(url): # get article id
    _aid = None
    rst = re.findall(r"^/news\/articles\/.+", url)
    if len(rst) > 0:
        _aid = rst[0].replace('/news/articles/', '')
        try:
            idx = _aid.index('#:')
            _aid = _aid[:idx]
        except:
            pass
    rst = re.findall(r"^https:\/\/www\.bbc\.com\/news\/articles\/.+", url)
    if len(rst) > 0:
        _aid =  rst[0].replace(f'{HOME_URL}/news/articles/', '')
        try:
            idx = _aid.index('#:')
            _aid = _aid[:idx]
        except:
            pass
    if _aid and not _aid.startswith('http'):
        return _aid
    return None

class Target:
    def __init__(self, word:str, lb:bool=False, rb:bool=False, cs:bool=True, target_cnt=TARGET_CNT):
        self.word = word
        self.lborder = lb
        self.rborder = rb
        self.case_sensitive = cs
        self.completed = False
        self.hit_urls = set()
        self.target_cnt = target_cnt

    def wrap_border(self, noun):
        pattern = noun.lower() if not self.case_sensitive else noun
        if self.lborder:
            pattern = r"\b" + pattern
        if self.rborder:
            pattern = pattern + r"\b"
        return pattern
    def get_kw(self):
        return self.word
    def search(self, pat, content):
        if self.case_sensitive:
            return re.search(pat, content)
        return re.search(pat, content, re.IGNORECASE)
    def hit(self, paragraph):
        pattern = self.wrap_border(self.word)
        if self.search(pattern, paragraph):
            return True
        return False
    def generate_prompt(self, hit_paras:list):
        kw = self.get_kw()
        idx = 1
        prompt = f'对于下面这篇英语文章\n'
        prompt += f'{idx}.为这篇德语文章生成一篇简短的中文摘要\n'; idx += 1
        for hp in hit_paras:
            prompt += f'{idx}.翻译第{hp}段，并用粗体标出用到‘{kw}’的句子\n'; idx += 1
            prompt += f'{idx}.打印原文第{hp}段，并用加粗斜体标记出用到了‘{kw}’的句子\n'; idx += 1
        return prompt


def parse_article(content, aid):
    global targets
    url = f'{HOME_URL}/news/articles/{aid}'
    doc = pq(content)
    page = doc('article')
    for target in targets:
        if target.completed or url in target.hit_urls:
            continue
        paragraphs = page('p')
        hit_flag = False
        paragraph_contents = []
        hit_paragraph_nos = set()
        for i, p in enumerate(paragraphs.items(), start=1):
            paragraph = p.text()
            paragraph_contents.append(paragraph)
            if target.hit(paragraph):
                hit_flag = True
                hit_paragraph_nos.add(i)

        if hit_flag and url not in target.hit_urls:
            print(f'hit {target.get_kw()} in {aid}' + (' ' * 100))
            fname = f'./{folder_path}/article-{target.get_kw()}-' + aid + '.txt'
            with open(fname, 'w+', encoding='utf8') as f:
                f.write(url + '\n')
                f.write(target.generate_prompt([str(p) for p in sorted(hit_paragraph_nos)]))
                for i, p in enumerate(paragraph_contents, start=1):
                    f.write(f'p{i}:\n')
                    f.write(p + '\n')
            target.hit_urls.add(url)
            if target.target_cnt == len(target.hit_urls):
                print(f'{target.get_kw()} complete!')
                target.completed = True

    article_ids[aid] = 1 # marked as searched
    # recruit other links
    anchors = doc('a')
    for a in anchors:
        if 'href' not in a.attrib:
            continue
        ref = a.attrib['href']
        _aid = gaid(ref)
        if _aid:
            article_ids[_aid] = 0
    progress_bar(targets)

def file_accessable(path):
    if isfile(path) and access(path, R_OK):
        return True
    return False

async def get_content_and_parse(aid):
    global received_bytes, cache_hit_cnt
    content = ''
    path = f'{cache_folder}/{aid}.html'
    if file_accessable(path):
        cache_hit_cnt += 1
        async with aiofiles.open(path, mode='r', encoding='utf8') as f:
            async for l in f:
                content += l
    else:
        url = f'{HOME_URL}/news/articles/{aid}'
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            resp = await client.get(url=url)
            content = resp.content
            received_bytes += len(content)
            with open(path, 'w+', encoding='utf8') as fw:
                fw.write(content.decode('utf8'))
    parse_article(content, aid)
    return aid

async def launch(async_fun, params):
    aids = await asyncio.gather(*map(async_fun, params))
    return aids

def delete_tmp_articles():
    global folder_path
    for filename in os.listdir(folder_path):
        if not filename.startswith('article-'):
            continue
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # 删除文件或符号链接
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # 删除子文件夹（可选）
        except Exception as e:
            print(f"删除 {file_path} 失败: {e}")

def zip_up_rst():
    global folder_path
    target_zip = f'/archive{datetime.now().strftime("%Y%m%d-%H%M%S")}.zip'
    with zipfile.ZipFile(folder_path + target_zip, 'w') as zipf:
        for filename in os.listdir(folder_path):
            if not filename.startswith('article-'):
                continue
            file_path = os.path.join(folder_path, filename)
            zipf.write(file_path)
    shutil.copyfile(f'{folder_path}/{target_zip}', f'{folder_path}/archive.zip')

def readable_byte_len(bl):
    if bl > 1024 * 1024 * 1024:
        return f'{float(bl)/(1024 * 1024 * 1024):0.2f} Gb'
    if bl > 1024 * 1024:
        return f'{float(bl)/(1024 * 1024):0.2f} Mb'
    if bl > 1024:
        return f'{float(bl)/(1024):0.2f} Kb'
    return f'{float(bl):0.2f} byte'

def progress_bar(targets):
    global tm1
    tm2 = time.perf_counter()
    s = ''
    for i, t in enumerate(targets, start=1):
        if i != 1:
            s += '|'
        s += ('〇' if t.completed else str(len(t.hit_urls)))
    bl = readable_byte_len(received_bytes)
    print(f'[{s}] {urls_info(1)} searched, {urls_info(0)} remain {tm2-tm1:0.2f} sec {bl} received\r', end='')

def urls_info(flg): # 1 searched; 0 remain
    global article_ids
    return len(([k for k, v in article_ids.items() if v == flg]))

def is_all_done(targets):
    for t in targets:
        if not t.completed:
            return False
    return True

def recruit_from_url(url):
    global article_ids
    response = requests.get(url)
    print(f'{url} : {response.status_code}')
    doc = pq(response.content)
    anchors = doc('a')
    for a in anchors:
        if 'href' not in a.attrib:
            continue
        ref = a.attrib['href']
        _aid = gaid(ref)
        if _aid:
            article_ids[_aid] = 0

def unsearched(aid):
    if aid not in article_ids:
        return True
    if article_ids[aid] == 0:
        return True
    return False

def start_crawl(targets):
    global article_ids
    delete_tmp_articles()

    recruit_from_url(HOME_URL)

    while not is_all_done(targets):
        aids1 = random.sample([k for k, v in article_ids.items() if v == 0], THREADS)
        aids2 = random.sample([k for k in cached_article_ids], THREADS)
        aids = [aid for aid in (aids1 + aids2) if unsearched(aid)]

        done_aids = asyncio.run(launch(get_content_and_parse, aids))
        for aid in done_aids:
            article_ids[aid] = 1
            if aid in cached_article_ids: cached_article_ids.remove(aid)
        progress_bar(targets)

    print(f'\n{urls_info(1)} article searched', end='\n')
    tm2 = time.perf_counter()
    print(f'totally {tm2-tm1:0.2f} sec used')
    bl = readable_byte_len(received_bytes)
    print(f'{bl} data received')
    print(f'{cache_hit_cnt} cache hit ({float(cache_hit_cnt * 100)/urls_info(1):.2f}%)')


if __name__ == '__main__':
    aid_json_file = 'bbc-aids.json'
    targets = [
            Target('promise'),
            Target('compromise'),
            Target('federal'),
            Target('spiritual'),
            Target('attachment'),
            ]

    # get init article ids from last history
    with open(aid_json_file, 'r', encoding='utf8') as fp:
        content = json.load(fp)
        for aid, _ in content.items():
            article_ids[aid] = 0
            path = f'{cache_folder}/{aid}.html'
            if file_accessable(path):
                cached_article_ids.add(aid)
    print(f'load urls from history: {len(article_ids)}')

    if len(targets) != 0:
        start_crawl(targets)

    zip_up_rst()
    delete_tmp_articles()

    # save article_ids
    with open(aid_json_file, 'w', encoding='utf8') as fp:
        json.dump(article_ids, fp)
