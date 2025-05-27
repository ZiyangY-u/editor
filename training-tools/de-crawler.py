#!/usr/bin/python3.8

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
import itertools
from pyquery import PyQuery as pq
from hashlib import sha256
from datetime import datetime

TIMEOUT = httpx.Timeout(360.0, connect=360.0)
PROXIES={ 'http': 'http://127.0.0.1:58591', 'https': 'http://127.0.0.1:58591', }
PROXY = 'http://127.0.0.1:58591'
HOME_URL = 'https://www.welt.de'

THREADS = 10
MAX_THREADS = 100

NOUN_MODE     = 1
VERB_MODE     = 2
SEP_VERB_MODE = 3
PHRASE_MODE   = 4
OTHER_MODE    = 9


TARGET_CNT = 5

to_search = {}
folder_path = './articles'
received_bytes = 0
net_request_time_usage = 0
tm1 = time.perf_counter()

def get_declension(noun):
    dkls = ''
    resp = requests.get(f'https://www.verbformen.com/declension/nouns/{noun}.htm')
    doc = pq(resp.content.decode('utf8'))
    declension_tbl = doc('.vDkl>.vTbl')
    for tbl in declension_tbl.items():
        dkls += ' '
        dkls += str(tbl('td').text())
    dkls = dkls.replace('\n', '')
    rst = set()
    for dkl in (dkl for dkl in dkls.split(' ')):
        if dkl in ['', 'der', 'des', 'dem', 'den', 'die', 'das']:
            continue
        if '/' in dkl:
            for d in (d for d in dkl.split('/')):
                rst.add(d.replace('⁰', '').replace('¹', '').replace('²', '').replace('³', '').replace('⁴', '').replace('⁵', '').replace('⁶', '').replace('⁷', '').replace('⁸', '').replace('⁹', ''))
        else:
            rst.add(dkl.replace('⁰', '').replace('¹', '').replace('²', '').replace('³', '').replace('⁴', '').replace('⁵', '').replace('⁶', '').replace('⁷', '').replace('⁸', '').replace('⁹', ''))
    print(f'noun target: {", ".join(dkl for dkl in rst)}')
    return rst

def get_conjuncated(verb, prefix):
    # resp = requests.get('https://api.verbix.com/conjugator/iv1/6153a464-b4f0-11ed-9ece-ee3761609078/1/13/113/' + verb, proxies=PROXIES)
    resp = requests.get('https://api.verbix.com/conjugator/iv1/6153a464-b4f0-11ed-9ece-ee3761609078/1/13/113/' + verb)
    content = json.loads(resp.content.decode('utf8'))
    # print(content['p1']['html'])

    doc = pq(content['p1']['html'])
    conjuncated = doc('span.normal')
    irregular = doc('span.irregular')
    targets = {verb}
    for c in itertools.chain(conjuncated.items(), irregular.items()):
        for w in (w.strip() for w in str(c.text()).split(' ')):
            if prefix == '':
                targets.add(w)
            elif w.startswith(prefix) and len(w) > len(prefix):
                targets.add(w)

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

    print(f'verb target: {", ".join(t for t in targets)}')

    return targets

class Target:
    def __init__(self, word:str, fix:str, lb:bool, rb:bool, cs:bool, mode, target_cnt=TARGET_CNT, prefix=''):
        self.key_noun_verb = word # noun or verb
        self.key_fix = fix
        self.lborder = lb # left border
        self.rborder = rb # right border
        self.case_sensitive = cs
        self.match_mode = mode
        self.hit_urls = {}
        self.target_cnt = target_cnt
        self.prefix = prefix
        if mode in (VERB_MODE, SEP_VERB_MODE):
            self.conjuncated = get_conjuncated(self.key_noun_verb, self.prefix)
            if len(self.conjuncated) == 0:
                print(f'can not conjuncate:{self.key_noun_verb}')
                exit(1)
        if mode == NOUN_MODE and self.key_noun_verb[0].isupper():
            self.declensions = get_declension(self.key_noun_verb)
            if len(self.declensions) == 0:
                print(f'can not declension:{self.key_noun_verb}')
                exit(1)

    def wrap_border(self, noun):
        pattern = noun.lower() if not self.case_sensitive else noun
        if self.lborder:
            pattern = r"\b" + pattern
        if self.rborder:
            pattern = pattern + r"\b"
        return pattern

    def hit(self, paragraph):
        if self.match_mode == NOUN_MODE:
            if self.key_noun_verb[0].isupper():
                for dkl in self.declensions:
                    pattern = self.wrap_border(dkl)
                    if re.search(pattern, (paragraph.lower() if not self.case_sensitive else paragraph)):
                        return True
                    return False
            else:
                pattern = self.wrap_border(self.key_noun_verb)
                if re.search(pattern, (paragraph.lower() if not self.case_sensitive else paragraph)):
                    return True
                return False
        if self.match_mode == VERB_MODE:
            for kw in self.conjuncated:
                pattern = r"\b" + kw.lower() + r"\b[^\.:,]*\b" + self.key_fix + r"\b"
                if re.search(pattern, paragraph.lower()):
                    return True
            for kw in self.conjuncated:
                pattern = r"\b" + self.key_fix + kw.lower() + r"\b"
                if re.search(pattern, paragraph.lower()):
                    return True
            return False
        if self.match_mode == SEP_VERB_MODE:
            for kw in self.conjuncated:
                pattern = r"\b" + kw.lower() + r"\b[^\.:,]*\b" + self.key_fix + r"\b"
                if re.search(pattern, paragraph.lower()):
                    return True
            for kw in self.conjuncated:
                pattern = r"\b" + self.key_fix + kw.lower() + r"\b"
                if re.search(pattern, paragraph.lower()): return True
                pattern = r"\b" + self.key_fix + 'zu' + kw.lower() + r"\b"
                if re.search(pattern, paragraph.lower()): return True
            return False
        if self.match_mode == PHRASE_MODE:
            pattern = r"\b" + self.key_fix + r"\b[^\.]*\b" + self.key_noun_verb + r"\b"
            if re.search(pattern, paragraph.lower()):
                return True
            return False

    def get_kw(self):
        kw = self.key_noun_verb
        if self.match_mode == VERB_MODE:
            kw = self.key_noun_verb
        if self.match_mode == SEP_VERB_MODE:
            kw = self.key_fix + self.key_noun_verb
        if self.match_mode == PHRASE_MODE:
            kw = self.key_fix + '...' + self.key_noun_verb
        return kw

    def generate_prompt(self, hit_paras:list):
        kw = self.get_kw()
        idx = 1
        prompt = f'对于下面这篇德语文章\n'
        prompt += f'{idx}.打印出‘{kw}’的音标(包括重音符号)'; idx += 1

        if self.match_mode == NOUN_MODE and self.key_noun_verb[0].isupper():
            prompt += f'以及阴阳性和复数形式\n';
        else:
            prompt += f'\n';

        prompt += f'{idx}.为这篇德语文章生成一篇简短的中文摘要\n'; idx += 1
        for hp in hit_paras:
            prompt += f'{idx}.翻译第{hp}段，并用粗体标出用到‘{kw}’的句子\n'; idx += 1
            prompt += f'{idx}.打印原文第{hp}段，并用加粗斜体标记出用到了‘{kw}’的句子\n'; idx += 1

        return prompt


def parse_article(content, url, targets):
    global to_search
    if 'video' in url or '/plus' in url: return 
    if deal_url(url) in to_search and to_search[deal_url(url)] == 1: return

    doc = pq(content)
    page = doc('.c-article-page__container')
    for target in targets:
        paragraphs = page('p')
        hit_flag = False
        if len(target.hit_urls) >= target.target_cnt or url in target.hit_urls:
            continue
        paragraph_contents = []
        hit_paragraph_nos = set()
        for i, p in enumerate(paragraphs.items(), start=1):
            paragraph = p.text()
            paragraph_contents.append(paragraph)
            if target.hit(paragraph):
                hit_flag = True
                hit_paragraph_nos.add(i)

        if hit_flag and url not in target.hit_urls:
            print(f'hit {target.get_kw()} in {url}')
            target.hit_urls[url] = 1
            fname = f'./articles/article-{target.get_kw()}-' + sha256(url.encode('utf8')).hexdigest() + '.txt'
            with open(fname, 'w+', encoding='utf8') as f:
                # f.write(url + '\n\n')
                f.write(target.generate_prompt([str(p) for p in sorted(hit_paragraph_nos)]))
                for i, p in enumerate(paragraph_contents, start=1):
                    f.write(f'p{i}:\n')
                    f.write(p + '\n')
            if target.target_cnt == len(target.hit_urls):
                print(f'{target.get_kw()} complete!')

    to_search[deal_url(url)] = 1
    # recruit other links
    anchors = doc('a')
    for a in anchors:
        if 'href' not in a.attrib:
            continue
        ref = a.attrib['href']
        if ref[0] == '/' and 'article' in ref and ref not in to_search:
            to_search[deal_url(ref)] = 0
    progress_bar(targets)

async def get_content(url):
    # print('requesting:', url)
    # async with httpx.AsyncClient(timeout=TIMEOUT, proxy=PROXY, follow_redirects=True) as client:
    async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
        return await client.get(url=url)

async def launch(async_fun, params):
    global received_bytes, net_request_time_usage
    req_tm1 = time.perf_counter()
    resps = await asyncio.gather(*map(async_fun, params))
    req_tm2 = time.perf_counter()
    byte_len = sum(len(resp.content) for resp in resps)
    print(f'\nreceived {len(params)} articles ({readable_byte_len(byte_len)}) in {req_tm2-req_tm1:0.2f} sec')
    net_request_time_usage += (req_tm2-req_tm1)
    received_bytes += byte_len
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
    global to_search
    return len(([k for k, v in to_search.items() if v == flg]))

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
    formatted_time = datetime.now().strftime("%Y%m%d-%H%M%S")
    with zipfile.ZipFile(folder_path + f'/archive{formatted_time}.zip', 'w') as zipf:
        for filename in os.listdir(folder_path):
            if not filename.startswith('article-'):
                continue
            file_path = os.path.join(folder_path, filename)
            zipf.write(file_path)

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
        s += ('〇' if len(t.hit_urls) == t.target_cnt else str(len(t.hit_urls)))
    bl = readable_byte_len(received_bytes)
    print(f'[{s}] {urls_info(1)} searched, {urls_info(0)} remain {tm2-tm1:0.2f} sec {bl} received\r', end='')

def is_all_done(targets):
    for t in targets:
        if len(t.hit_urls) < t.target_cnt:
            return False
    return True

def get_next_batch_count():
    global THREADS
    next_threads = THREADS + 5 if THREADS + 5 < MAX_THREADS else MAX_THREADS
    if next_threads > urls_info(0):
        THREADS = 5
    else :
        THREADS = next_threads

def start_crawl(targets):
    global to_search
    delete_tmp_articles()

    # response = requests.get(HOME_URL, proxies=PROXIES)
    response = requests.get(HOME_URL)
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
        get_next_batch_count()
        urls = random.sample([k for k, v in to_search.items() if v == 0], THREADS)
        results = asyncio.run(launch(get_content, urls))
        for rst in results:
            parse_article(rst.content, str(rst.url), targets)
            to_search[deal_url(str(rst.url))] = 1
        for url in urls: # mark as searched
            to_search[deal_url(url)] = 1
        progress_bar(targets)

    print(f'\n{urls_info(1)} article searched', end='\n')
    tm2 = time.perf_counter()
    print(f'totally {tm2-tm1:0.2f} sec (net request: {net_request_time_usage:.2f} sec {float(net_request_time_usage)*100/(tm2-tm1):.2f}%) used')
    bl = readable_byte_len(received_bytes)
    print(f'{bl} data received')

if __name__ == '__main__':
    targets = [
            ]

    if len(targets) != 0:
        start_crawl(targets)
    zip_up_rst()
    delete_tmp_articles()

