#!/usr/bin/python3.8

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

NOUN_MODE     = 1
VERB_MODE     = 2
SEP_VERB_MODE = 3


TARGET_CNT = 5

to_search = {}

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

    targets.discard('bin')
    targets.discard('bist')
    targets.discard('ist')
    targets.discard('sei')
    targets.discard('seid')
    targets.discard('seien')
    targets.discard('seiest')
    targets.discard('seiet')
    targets.discard('sein')
    targets.discard('sind')
    targets.discard('war')
    targets.discard('waren')
    targets.discard('warst')
    targets.discard('wart')
    targets.discard('wäre')
    targets.discard('wären')
    targets.discard('wärest')
    targets.discard('wäret')

    # print('verb targets:')
    # for t in targets:
    #     print(t, end=' ')
    # print()

    return targets

class Target:
    def __init__(self, word:str, fix:str, lb:bool, rb:bool, cs:bool, mode):
        self.key_noun_verb = word # noun or verb
        self.key_fix = fix
        self.lborder = lb # left border
        self.rborder = rb # right border
        self.case_sensitive = cs
        self.match_mode = mode
        self.hit_cnt = 0
        if mode in (VERB_MODE, SEP_VERB_MODE):
            self.conjuncated = get_conjuncated(self.key_noun_verb)

    def hit(self, paragraph):
        if self.match_mode == NOUN_MODE:
            pattern = self.key_noun_verb.lower() if not self.case_sensitive else self.key_noun_verb
            if self.lborder:
                pattern = r"\b" + pattern
            if self.rborder:
                pattern = pattern + r"\b"
            if re.search(pattern, (paragraph.lower() if not self.case_sensitive else paragraph)):
                return True
            return False
        if self.match_mode == VERB_MODE:
            for kw in self.conjuncated:
                pattern = r"\b" + kw.lower() + r"\b[^\.]*\b" + self.key_fix + r"\b"
                if re.search(pattern, paragraph.lower()):
                    return True
            for kw in self.conjuncated:
                pattern = r"\b" + self.key_fix + kw.lower() + r"\b"
                if re.search(pattern, paragraph.lower()):
                    return True
            return False
        if self.match_mode == SEP_VERB_MODE:
            for kw in self.conjuncated:
                pattern = r"\b" + kw.lower() + r"\b[^\.]*\b" + self.key_fix + r"\b"
                if re.search(pattern, paragraph.lower()):
                    return True
            for kw in self.conjuncated:
                pattern = r"\b" + self.key_fix + kw.lower() + r"\b"
                if re.search(pattern, paragraph.lower()):
                    return True
            return False

    def generate_propt(self, hit_paras:list):
        kw = self.key_noun_verb
        idx = 1
        if self.match_mode == VERB_MODE:
            kw = self.key_noun_verb
        if self.match_mode == SEP_VERB_MODE:
            kw = self.key_fix + self.key_noun_verb
        prompt = f'对于下面这篇德语文章\n'
        prompt += f'{idx}.为这篇德语文章生成一篇中文摘要\n'
        idx += 1
        for hp in hit_paras:
            prompt += f'{idx}.翻译第{hp}段，并用粗体标出用到‘{kw}’的句子\n'
            idx += 1
            prompt += f'{idx}.打印原文第{hp}段，并用加粗斜体标记出用到了‘{kw}’的句子\n'
            idx += 1

        return prompt


def parse_article(content, url, targets):
    global hit_cnt
    if 'video' in url or '/plus' in url: return 

    doc = pq(content)
    page = doc('.c-article-page__container')
    paragraphs = page('p')
    for target in targets:
        hit_flag = False
        if target.hit_cnt >= TARGET_CNT:
            continue
        paragraph_contents = []
        hit_paragraph_nos = set()
        for i, p in enumerate(paragraphs.items(), start=1):
            paragraph = p.text()
            paragraph_contents.append(paragraph)
            if target.hit(paragraph):
                hit_flag = True
                hit_paragraph_nos.add(i)

        if hit_flag:
            target.hit_cnt += 1
            # print(f'{hit_cnt} hit in:{url}', end='\n')
            fname = f'./articles/article-{target.key_fix + target.key_noun_verb}-' + sha256(url.encode('utf8')).hexdigest() + '.txt'
            with open(fname, 'w+', encoding='utf8') as f:
                # f.write(url + '\n\n')
                f.write(target.generate_propt([str(p) for p in sorted(hit_paragraph_nos)]))
                for i, p in enumerate(paragraph_contents, start=1):
                    f.write(f'p{i}:\n')
                    f.write(p + '\n')

    # recruit other links
    anchors = doc('a')
    for a in anchors:
        ref = a.attrib['href']
        if ref[0] == '/' and 'article' in ref and ref not in to_search:
            to_search[deal_url(ref)] = 0

async def get_content(url):
    # print('requesting:', url)
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

def progress_bar(targets):
    s = ''
    for i, t in enumerate(targets, start=1):
        rest_cnt = TARGET_CNT - t.hit_cnt
        if i != 1:
            s += '|'
        s += ('○' * t.hit_cnt + '-' * rest_cnt)
    return f"[{s}]"

def is_all_done(targets):
    for t in targets:
        if t.hit_cnt < TARGET_CNT:
            return False
    return True

def start_crawl(targets):
    delete_tmp_articles()

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

    while not is_all_done(targets):
        urls = random.sample([k for k, v in to_search.items() if v == 0], THREADS if urls_info(0) > THREADS else 5)
        results = asyncio.run(launch(get_content, urls))
        for rst in results:
            parse_article(rst.content, str(rst.url), targets)
        for url in urls: # mark as searched
            to_search[url] = 1
        tm2 = time.perf_counter()
        print(f'{progress_bar(targets)} {urls_info(1)} searched, {urls_info(0)} remain {tm2-tm1:0.2f} sec\r', end='')

    print(f'\n{urls_info(1)} article searched', end='\n')
    tm2 = time.perf_counter()
    print(f'{tm2-tm1:0.2f} sec used')

if __name__ == '__main__':
    targets = [
            Target(word='Bahn', fix='', lb=False, rb=False, cs=True, mode=NOUN_MODE),
            Target(word='falsch', fix='', lb=False, rb=False, cs=True, mode=NOUN_MODE),
            Target(word='Fisch', fix='', lb=False, rb=False, cs=True, mode=NOUN_MODE),
            Target(word='Formular', fix='', lb=False, rb=False, cs=True, mode=NOUN_MODE),
            Target(word='Gewicht', fix='', lb=False, rb=False, cs=True, mode=NOUN_MODE),
            Target(word='Reis', fix='', lb=False, rb=False, cs=True, mode=NOUN_MODE),
            Target(word='Uhr', fix='', lb=False, rb=False, cs=True, mode=NOUN_MODE),
            Target(word='verdienen', fix='', lb=False, rb=False, cs=True, mode=VERB_MODE),
            ]

    if len(targets) != 0:
        start_crawl(targets)
