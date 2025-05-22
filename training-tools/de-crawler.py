#!/usr/bin/python3

import requests
import asyncio
import httpx
import re
import json
import time
import os
import shutil
import random
from pyquery import PyQuery as pq
from hashlib import sha256

TIMEOUT = httpx.Timeout(360.0, connect=360.0)
PROXIES={ 'http': 'http://127.0.0.1:58591', 'https': 'http://127.0.0.1:58591', }
PROXY = 'http://127.0.0.1:58591'
HOME_URL = 'https://www.welt.de'

THREADS = 20
KEY_NOUN = 'kopf'
KEY_VERB = 'verkaufen'
KEY_FIX = 'an'

NOUN_MODE     = 1
VERB_MODE     = 2
SEP_VERB_MODE = 3

MATCH_MODE = 1

TARGET_CNT = 5

to_search = {}
hit_cnt = 0
conjuncated = {}

def get_conjuncated(verb):
    resp = requests.get('https://api.verbix.com/conjugator/iv1/6153a464-b4f0-11ed-9ece-ee3761609078/1/13/113/' + verb, proxies=PROXIES)
    content = json.loads(resp.content.decode('utf8'))
    # print(content['p1']['html'])

    doc = pq(content['p1']['html'])
    conjuncated = doc('span.normal')
    irregular = doc('span.irregular')
    targets = {verb}
    for c in conjuncated.items():
        for w in c.text().split(' '):
            targets.add(w.strip())
    for i in irregular.items():
        for w in i.text().split(' '):
            targets.add(w.strip())
    targets.discard('habe')
    targets.discard('hast')
    targets.discard('hat')
    targets.discard('haben')
    targets.discard('habt')
    targets.discard('habet')
    targets.discard('habest')

    targets.discard('hatte')
    targets.discard('hattest')
    targets.discard('hatten')
    targets.discard('hattet')

    targets.discard('hätte')
    targets.discard('hättest')
    targets.discard('hätte')
    targets.discard('hätten')
    targets.discard('hättet')

    targets.discard('werde')
    targets.discard('wirst')
    targets.discard('wird')
    targets.discard('werden')
    targets.discard('werdet')
    targets.discard('werden')

    targets.discard('würde')
    targets.discard('würdest')
    targets.discard('würde')
    targets.discard('würden')
    targets.discard('würdet')
    targets.discard('würden')
    targets.discard('-')
    print('verb targets:')
    for t in targets:
        print(t, end=' ')
    print()

    return targets

def hit_noun(paragraph) -> bool:
    if re.search(KEY_NOUN.lower(), paragraph.lower()):
        return True
    return False

def hit_verb(paragraph) -> bool:
    for kw in conjuncated:
        pattern = r"\b" + kw.lower() + r"\b"
        if re.search(pattern, paragraph.lower()):
            return True
    return False

def hit_sep_verb(paragraph) -> bool:
    for kw in conjuncated:
        pattern = r"\b" + kw.lower() + r"\b[^\.]*\b" + KEY_FIX + r"\b"
        if re.search(pattern, paragraph.lower()):
            return True
    for kw in conjuncated:
        pattern = r"\b" + KEY_FIX + kw.lower() + r"\b"
        if re.search(pattern, paragraph.lower()):
            return True
    return False

def hit(paragraph):
    if MATCH_MODE == NOUN_MODE and hit_noun(paragraph):
        return True
    if MATCH_MODE == VERB_MODE and hit_verb(paragraph):
        return True
    if MATCH_MODE == SEP_VERB_MODE and hit_sep_verb(paragraph):
        return True
    return False


def parse_article(content, url):
    global hit_cnt
    hit_flag = False
    if 'video' in url or '/plus' in url: return 
    
    try:
        doc = pq(content)
    except:
        print(content)
        print(url)
        return
    page = doc('.c-article-page__container')
    paragraphs = page('p')
    paragraph_contents = []
    hit_paragraph_nos = set()
    for i, p in enumerate(paragraphs.items(), start=1):
        paragraph = p.text()
        paragraph_contents.append(paragraph)
        if hit(paragraph):
            hit_paragraph_nos.add(i)
            print(f'hit in paragraph {i}:--------------------')
            # print(p.text())
            hit_flag = True

    if hit_flag:
        hit_cnt += 1
        print('hit in:', url, end='\n\n')
        fname = './articles/article-' + sha256(url.encode('utf8')).hexdigest() + '.txt'
        with open(fname, 'w+') as f:
            f.write(url + '\n\n')
            f.write(f'帮我为这篇德语文章生成一篇摘要，并翻译第{"，".join(str(p) for p in hit_paragraph_nos)}段' + '\n')
            for i, p in enumerate(paragraph_contents, start=1):
                f.write(f'***p{i}:\n' if i in hit_paragraph_nos else f'p{i}:\n')
                f.write(p + '\n')

    # recruit other links
    anchors = doc('a')
    for a in anchors:
        ref = a.attrib['href']
        if ref[0] == '/' and 'article' in ref and ref not in to_search:
            to_search[deal_url(ref)] = 0

async def get_content(url):
    async with httpx.AsyncClient(timeout=TIMEOUT, proxy=PROXY, follow_redirects=True) as client:
        return await client.get(url=url)

async def launch(async_fun, params):
    resps = await asyncio.gather(*map(async_fun, params))
    # contents = [resp.content for resp in resps]
    return resps

def deal_url(url):
    search_url = url if url[:4] == 'http' else HOME_URL + url
    try:
        idx = search_url.index('#:')
        search_url = search_url[:idx]
    except:
        pass
    return search_url

def print_search_mode():
    if MATCH_MODE == NOUN_MODE:
        print(f'search in noun mode, target: {KEY_NOUN}')
    if MATCH_MODE == VERB_MODE:
        print(f'search in verb mode, target: {KEY_VERB}')
    if MATCH_MODE == SEP_VERB_MODE:
        print(f'search in separate verb mode target: {KEY_FIX}{KEY_VERB}')
    
def urls_info(flg):
    # flg = 1 searched
    # flg = 0 remain
    return len(([k for k, v in to_search.items() if v == flg]))

def delete_tmp_articles():
    folder_path = './articles'
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


def start_crawl():
    delete_tmp_articles()
    print_search_mode()

    tm1 = time.perf_counter()
    response = requests.get(HOME_URL, proxies=PROXIES)
    print(response.status_code)
    doc = pq(response.content)
    articles = doc('#main').find('article').items()
    for article in articles:
        overline = article('div.c-teaser__container.is-full-height-flex > div.c-teaser__overline > div')
        preminum_flag = overline.children('.is-premium')
        title = article('div.c-teaser__container.is-full-height-flex > div.c-teaser__body > h4 > a')
        if not preminum_flag and title.attr('href') is not None:
            url = title.attr('href')
            if url not in to_search:
                to_search[deal_url(url)] = 0

    while hit_cnt < TARGET_CNT:
        urls = random.sample([k for k, v in to_search.items() if v == 0], THREADS)
        results = asyncio.run(launch(get_content, urls))
        for rst in results:
            parse_article(rst.content, str(rst.url))
        for url in urls: # mark as searched
            to_search[url] = 1
        tm2 = time.perf_counter()
        print(f'{urls_info(1)} article searched, {urls_info(0)} remain {tm2-tm1:0.2f} sec\r', end='')

    print(f'{urls_info(1)} article searched', end='\n')
    tm2 = time.perf_counter()
    print(f'{tm2-tm1:0.2f} sec used')

if __name__ == '__main__':
    if MATCH_MODE in (VERB_MODE, SEP_VERB_MODE):
        conjuncated = get_conjuncated(KEY_VERB)
    start_crawl()
