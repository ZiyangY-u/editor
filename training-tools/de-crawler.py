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
import aiofiles
from os import access, R_OK
from os.path import isfile
from pyquery import PyQuery as pq
from datetime import datetime

TIMEOUT = httpx.Timeout(360.0, connect=360.0)
PROXIES={ 'http': 'http://127.0.0.1:58591', 'https': 'http://127.0.0.1:58591', }
PROXY = 'http://127.0.0.1:58591'

THREADS = 15
MAX_THREADS = 100

NOUN_MODE     = 1
VERB_MODE     = 2
SEP_VERB_MODE = 3
PHRASE_MODE   = 4
OTHER_MODE    = 9


TARGET_CNT = 5

article_ids = {}
cached_article_ids = set()
# die Welt
WELT_HOME_URL = 'https://www.welt.de'
WELT_AID_TYPE = 10
# der Spiegel
SPIEGEL_HOME_URL = 'https://www.spiegel.de/'
plus_spiegel_aids = {}
SPIEGEL_AID_TYPE = 20
spiegel_aid_re = r'a-[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}'
spiegel_plus_hint = 'SPIEGEL+ wird über Ihren iTunes-Account abgewickelt und mit Kaufbestätigung bezahlt.'


targets = []

folder_path = './articles'
cache_folder = './cache'

received_bytes = 0
cache_hit_cnt = 0
tm1 = time.perf_counter()

black_list = {
        '252e57edaecec83003631c80e44de65baa14f041d2ed7387782a7a404da9c858',
        'b23a07cac215495cc43af0a77ec764f3f1ef558e15add298deb36843258e38d4',
        }

def _gaid(rst):
    _aid = rst[0]
    try:
        idx = _aid.index('#:')
        _aid = _aid[:idx]
        return _aid
    except:
        pass
    return None

def gaid(url): # get article id
    rst = re.findall(r"article\d+", url)
    if len(rst) > 0:
        return _gaid(rst)
    rst = re.findall(spiegel_aid_re, url)
    if len(rst) > 0:
        return _gaid(rst)
    return None

def get_declension2(noun):
    rst = set()
    resp = requests.get(f'https://en.wiktionary.org/wiki/{noun}')
    doc = pq(resp.content.decode('utf8'))
    tbl = doc('.inflection-table-de')
    tds = tbl('td')
    for td in tds.items():
        txt = str(td.text())
        if txt in { 'das', 'dem', 'den', 'der', 'des', 'die', 'ein', 'eine', 'einem', 'einen', 'einer', 'eines' }:
            continue
        if ',' in txt:
            for d in (d for d in txt.split(',')):
                rst.add(d.strip().replace('0', '').replace('1', '').replace('2', '').replace('3', '').replace('4', '').replace('5', '').replace('6', '').replace('7', '').replace('8', '').replace('9', ''))
        else:
            rst.add(txt.strip().replace('0', '').replace('1', '').replace('2', '').replace('3', '').replace('4', '').replace('5', '').replace('6', '').replace('7', '').replace('8', '').replace('9', ''))
    print(f'noun target: {", ".join(dkl for dkl in rst)}')
    return rst

def get_declension(noun):
    global received_bytes
    # time.sleep(random.randint(1, 5))
    dkls = ''
    resp = requests.get(f'https://www.verbformen.com/declension/nouns/{noun}.htm')
    received_bytes += len(resp.content)
    doc = pq(resp.content.decode('utf8'))
    declension_tbl = doc('.vDkl>.vTbl')
    for tbl in declension_tbl.items():
        dkls += ' '
        dkls += str(tbl('td').text())
    dkls = dkls.replace('\n', '')
    rst = set()
    for dkl in (dkl for dkl in dkls.split(' ')):
        if dkl in ['', 'der', 'des', 'dem', 'den', 'die', 'das', '-']:
            continue
        if '/' in dkl:
            for d in (d for d in dkl.split('/')):
                rst.add(d.replace('⁰', '').replace('¹', '').replace('²', '').replace('³', '').replace('⁴', '').replace('⁵', '').replace('⁶', '').replace('⁷', '').replace('⁸', '').replace('⁹', ''))
        else:
            rst.add(dkl.replace('⁰', '').replace('¹', '').replace('²', '').replace('³', '').replace('⁴', '').replace('⁵', '').replace('⁶', '').replace('⁷', '').replace('⁸', '').replace('⁹', ''))
    print(f'noun target: {", ".join(dkl for dkl in rst)}')
    return rst

def get_conjuncated(verb, prefix):
    # time.sleep(random.randint(1, 5))
    # resp = requests.get('https://api.verbix.com/conjugator/iv1/6153a464-b4f0-11ed-9ece-ee3761609078/1/13/113/' + verb, proxies=PROXIES)
    resp = requests.get('https://api.verbix.com/conjugator/iv1/6153a464-b4f0-11ed-9ece-ee3761609078/1/13/113/' + verb)
    content = json.loads(resp.content.decode('utf8'))
    # print(content['p1']['html'])

    doc = pq(content['p1']['html'])
    conjuncated = doc('span.normal')
    irregular = doc('span.irregular')
    verbs = {verb}
    for c in itertools.chain(conjuncated.items(), irregular.items()):
        for w in (w.strip() for w in str(c.text()).split(' ')):
            if prefix == '':
                verbs.add(w)
            elif w.startswith(prefix) and len(w) > len(prefix):
                verbs.add(w)

    verbs.discard('habe')
    verbs.discard('hast')
    verbs.discard('hat')
    verbs.discard('haben')
    verbs.discard('habt')
    verbs.discard('habet')
    verbs.discard('habest')

    verbs.discard('hatte')
    verbs.discard('hattest')
    verbs.discard('hatten')
    verbs.discard('hattet')

    verbs.discard('hätte')
    verbs.discard('hättest')
    verbs.discard('hätte')
    verbs.discard('hätten')
    verbs.discard('hättet')

    verbs.discard('werde')
    verbs.discard('wirst')
    verbs.discard('wird')
    verbs.discard('werden')
    verbs.discard('werdet')
    verbs.discard('werden')

    verbs.discard('würde')
    verbs.discard('würdest')
    verbs.discard('würde')
    verbs.discard('würden')
    verbs.discard('würdet')
    verbs.discard('würden')
    verbs.discard('-')

    verbs.discard('bin')
    verbs.discard('bist')
    verbs.discard('ist')
    verbs.discard('sei')
    verbs.discard('seid')
    verbs.discard('seien')
    verbs.discard('seiest')
    verbs.discard('seiet')
    verbs.discard('sein')
    verbs.discard('sind')
    verbs.discard('war')
    verbs.discard('waren')
    verbs.discard('warst')
    verbs.discard('wart')
    verbs.discard('wäre')
    verbs.discard('wären')
    verbs.discard('wärest')
    verbs.discard('wäret')

    print(f'verb target: {", ".join(t for t in verbs)}')

    return verbs

class Target:
    def __init__(self, word:str, fix:str, lb:bool, rb:bool, cs:bool, mode, target_cnt=TARGET_CNT, prefix=''):
        self.key_noun_verb = word # noun or verb
        self.key_fix = fix
        self.lborder = lb # left border
        self.rborder = rb # right border
        self.case_sensitive = cs
        self.match_mode = mode
        self.hit_urls = set()
        self.target_cnt = target_cnt
        self.prefix = prefix
        self.completed = False
        self.true_noun = False
        if mode in (VERB_MODE, SEP_VERB_MODE):
            self.conjuncated = get_conjuncated(self.key_noun_verb, self.prefix)
            if len(self.conjuncated) == 0:
                print(f'can not conjuncate:{self.key_noun_verb}')
                exit(1)
        if mode == NOUN_MODE and self.key_noun_verb[0].isupper():
            self.true_noun = True
            self.declensions = get_declension2(self.key_noun_verb)
            if len(self.declensions) == 0:
                print(f'can not declension:{self.key_noun_verb}')
                self.true_noun = False

    def wrap_border(self, noun):
        pattern = noun.lower() if not self.case_sensitive else noun
        if self.lborder:
            pattern = r"\b" + pattern
        if self.rborder:
            pattern = pattern + r"\b"
        return pattern

    def search(self, pat, content):
        if self.case_sensitive:
            return re.search(pat, content)
        return re.search(pat, content, re.IGNORECASE)

    def hit(self, paragraph):
        if self.match_mode == NOUN_MODE:
            if self.true_noun:
                for dkl in self.declensions:
                    pattern = self.wrap_border(dkl)
                    if self.search(pattern, paragraph):
                        return True
                    return False
            else:
                pattern = self.wrap_border(self.key_noun_verb)
                if self.search(pattern, paragraph):
                    return True
                return False
        if self.match_mode == VERB_MODE:
            for kw in self.conjuncated:
                pattern = r"\b" + kw.lower() + r"\b[^\.:,]*\b" + self.key_fix + r"\b"
                if self.search(pattern, paragraph):
                    return True
            for kw in self.conjuncated:
                pattern = r"\b" + self.key_fix + kw.lower() + r"\b"
                if self.search(pattern, paragraph):
                    return True
            return False
        if self.match_mode == SEP_VERB_MODE:
            for kw in self.conjuncated:
                pattern = r"\b" + kw.lower() + r"\b[^\.:,]*\b" + self.key_fix + r"\b"
                if self.search(pattern, paragraph):
                    return True
            for kw in self.conjuncated:
                pattern = r"\b" + self.key_fix + kw.lower() + r"\b"
                if self.search(pattern, paragraph): return True
                pattern = r"\b" + self.key_fix + 'zu' + kw.lower() + r"\b"
                if self.search(pattern, paragraph): return True
            return False
        if self.match_mode == PHRASE_MODE:
            pattern = r"\b" + self.key_fix + r"\b[^\.]*\b" + self.key_noun_verb + r"\b"
            if self.search(pattern, paragraph):
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

        if self.true_noun:
            prompt += f'以及阴阳性和复数形式\n';
        else:
            prompt += f'\n';

        prompt += f'{idx}.为这篇德语文章生成一篇简短的中文摘要\n'; idx += 1
        for hp in hit_paras:
            prompt += f'{idx}.翻译第{hp}段，并用粗体标出用到‘{kw}’的句子\n'; idx += 1
            prompt += f'{idx}.打印原文第{hp}段，并用加粗斜体标记出用到了‘{kw}’的句子\n'; idx += 1

        return prompt

def process_hit(target, aid, url, paragraph_contents, hit_paragraph_nos):
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
        print(f'{target.get_kw()} complete! at {datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}')
        target.completed = True

def parse_welt_article(content, aid):
    global targets
    url = determine_url_by_aid(aid)
    doc = pq(content)
    page = doc('.c-article-page__container')
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
            process_hit(target, aid, url, paragraph_contents, hit_paragraph_nos)

def parse_spiegel_article(content, aid):
    global spiegel_plus_hint
    if aid in plus_spiegel_aids:
        return
    url = determine_url_by_aid(aid)
    doc = pq(content)
    for target in targets:
        if target.completed or url in target.hit_urls:
            continue
        paragraphs = doc('p')
        title = doc('#Inhalt > article > header')
        hit_flag = False
        paragraph_contents = [str(title.text())]
        hit_paragraph_nos = set()
        for i, p in enumerate(paragraphs.items(), start=1):
            paragraph = str(p.text())
            if paragraph.startswith(spiegel_plus_hint):
                plus_spiegel_aids[aid] = 1
                print('skip spiegel plus article', aid)
                return
            paragraph_contents.append(paragraph)
            if target.hit(paragraph):
                hit_flag = True
                hit_paragraph_nos.add(i)
        if hit_flag and url not in target.hit_urls:
            process_hit(target, aid, url, paragraph_contents, hit_paragraph_nos)

def parse_article(content, aid):
    global targets
    recruit_from_content(content)
    type = determine_type_by_aid(aid)
    if type == WELT_AID_TYPE:
        parse_welt_article(content, aid)
    if type == SPIEGEL_AID_TYPE:
        parse_spiegel_article(content, aid)

    article_ids[aid] = 1 # marked as searched
    # recruit other links
    progress_bar(targets)

def file_accessable(path):
    if isfile(path) and access(path, R_OK):
        return True
    return False

async def recruit_url(aid):
    global received_bytes
    url = f'{WELT_HOME_URL}/{aid}'
    async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
        resp = await client.get(url=url)
        received_bytes += len(resp.content)
        recruit_from_content(resp.content)
        article_ids[aid] = 1 # mark as searched

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
        url = determine_url_by_aid(aid)
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

def urls_info(flg): # 1 searched; 0 remain
    global article_ids
    return len(([k for k, v in article_ids.items() if v == flg]))

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
    progress = f'[{s}] {urls_info(1)} searched, {urls_info(0)} remain {tm2-tm1:0.2f} sec {bl} received'
    progress += f' {datetime.now().strftime("%m/%d/%Y %H:%M:%S")}'
    print(f'{progress}\r', end='')

def is_all_done(targets):
    for t in targets:
        if not t.completed:
            return False
    return True

def recruit_from_url(url):
    global article_ids, received_bytes
    response = requests.get(url)
    # print(f'{url} : {response.status_code}')
    received_bytes += len(response.content)
    recruit_from_content(response.content)

def recruit_from_content(content):
    doc = pq(content)
    anchors = doc('a')
    for a in anchors:
        if 'href' not in a.attrib:
            continue
        ref = a.attrib['href']
        _aid = gaid(ref)
        if (ref[0] == '/' or ref.startswith(WELT_HOME_URL) or ref.startswith(SPIEGEL_HOME_URL)) and _aid and _aid not in article_ids:
            article_ids[_aid] = 0 # recruit url

def unsearched(aid):
    if aid not in article_ids:
        return True
    if article_ids[aid] == 0:
        return True
    return False

def determine_url_by_aid(aid):
    if re.match(spiegel_aid_re, aid):
        return SPIEGEL_HOME_URL + '/' + aid
    else:
        return WELT_HOME_URL + '/' + aid

def determine_type_by_aid(aid):
    if re.match(spiegel_aid_re, aid):
        return SPIEGEL_AID_TYPE
    else:
        return WELT_AID_TYPE

def recruit_from_home():
    recruit_from_url(WELT_HOME_URL)
    recruit_from_url(SPIEGEL_HOME_URL)
    # recruit_from_url(WELT_HOME_URL + '/wirtschaft/')
    # recruit_from_url(WELT_HOME_URL + '/iconist/')
    # recruit_from_url(WELT_HOME_URL + '/sport/')
    # recruit_from_url(WELT_HOME_URL + '/vermischtes/')
    # recruit_from_url(WELT_HOME_URL + '/politik/')
    # recruit_from_url(WELT_HOME_URL + '/debatte/')
    # recruit_from_url(WELT_HOME_URL + '/kultur/')
    # recruit_from_url(WELT_HOME_URL + '/gesundheit/')
    # recruit_from_url(WELT_HOME_URL + '/geschichte/')
    # recruit_from_url(WELT_HOME_URL + '/reise/')
    # recruit_from_url(WELT_HOME_URL + '/regionales/')
    # recruit_from_url(WELT_HOME_URL + '/sonderthemen/')

# def only_recruit(target_recruit_cnt):
#     init_size = len(article_ids)
#     recruit_from_home()
#     recruited = len(article_ids) - init_size
#     while recruited <= target_recruit_cnt and urls_info(0) > THREADS:
#         snapshot = recruited
#         aids = random.sample([k for k, v in article_ids.items() if v == 0], THREADS)
#         asyncio.run(launch(recruit_url, aids))
#         after_size = len(article_ids)
#         recruited = (after_size - init_size)
#         if snapshot != recruited:
#             print(f'{target_recruit_cnt - recruited} remain')
#         progress_bar([])

def start_crawl(targets):
    delete_tmp_articles()
    recruit_from_home()

    while not is_all_done(targets) and urls_info(0) > THREADS:
        _tmp = [k for k, v in article_ids.items() if v == 0 and k not in cached_article_ids and k not in plus_spiegel_aids]
        aids1 = random.sample(_tmp, THREADS) if len(_tmp) > THREADS else []
        aids2 = random.sample([k for k in cached_article_ids], THREADS) if len(cached_article_ids) > THREADS else []
        aids = [aid for aid in (aids1 + aids2) if unsearched(aid)]

        done_aids = asyncio.run(launch(get_content_and_parse, aids))
        for aid in done_aids:
            article_ids[aid] = 1

        progress_bar(targets)

    print(f'\n{urls_info(1)} article searched', end='\n')
    tm2 = time.perf_counter()
    print(f'totally {tm2-tm1:0.2f} sec used')
    bl = readable_byte_len(received_bytes)
    print(f'{bl} data received')
    print(f'{cache_hit_cnt} cache hit ({float(cache_hit_cnt * 100)/urls_info(1):.2f}%)')
    # print incomplete target(s)
    for t in targets:
        if not t.completed:
            print(t.get_kw(), 'not completed', end='\n')

if __name__ == '__main__':
    welt_aid_json_file = 'welt-aids.json'
    plus_aid_json_file = 'plus-aids.json'

    targets = [

            # Target(word='Wertschöpfungskette', fix='', lb=False, rb=False, cs=False, mode=NOUN_MODE),
            # Target(word='angegriffen', fix='', lb=False, rb=False, cs=False, mode=NOUN_MODE),
            # Target(word='angepöbelt', fix='', lb=False, rb=False, cs=False, mode=NOUN_MODE),
            # Target(word='tuscheln', fix='', lb=False, rb=False, cs=True, mode=VERB_MODE),
            # Target(word='kichern', fix='', lb=False, rb=False, cs=True, mode=VERB_MODE),
            # Target(word='Bloßstellung', fix='', lb=False, rb=False, cs=False, mode=NOUN_MODE),
            # Target(word='aufbereitet', fix='', lb=False, rb=False, cs=False, mode=NOUN_MODE),
            # Target(word='entwenden', fix='', lb=False, rb=False, cs=True, mode=VERB_MODE),
            # Target(word='versehen', fix='', lb=False, rb=False, cs=True, mode=VERB_MODE),
            # Target(word='durchforsten', fix='', lb=False, rb=False, cs=True, mode=VERB_MODE),
            # Target(word='Abhilfe', fix='', lb=False, rb=False, cs=False, mode=NOUN_MODE),
            # Target(word='theologisch', fix='', lb=False, rb=False, cs=False, mode=NOUN_MODE),
            # Target(word='Akronym', fix='', lb=False, rb=False, cs=False, mode=NOUN_MODE),
            # Target(word='entfernungungsradius', fix='', lb=False, rb=False, cs=False, mode=NOUN_MODE),
            # Target(word='Baugewerbe', fix='', lb=False, rb=False, cs=False, mode=NOUN_MODE),
            # Target(word='Akzentuierung', fix='', lb=False, rb=False, cs=False, mode=NOUN_MODE),
            # Target(word='Ausgleichszahlung', fix='', lb=False, rb=False, cs=False, mode=NOUN_MODE),
            # Target(word='Bronchitis', fix='', lb=False, rb=False, cs=False, mode=NOUN_MODE),
            # Target(word='gesamtfiskalich', fix='', lb=False, rb=False, cs=False, mode=NOUN_MODE),
            # Target(word='delegieren', fix='', lb=False, rb=False, cs=True, mode=VERB_MODE),
            # Target(word='Pappe', fix='', lb=False, rb=False, cs=False, mode=NOUN_MODE),
            # Target(word='Schaltkreis', fix='', lb=False, rb=False, cs=False, mode=NOUN_MODE),
            # Target(word='verschlüsselt', fix='', lb=False, rb=False, cs=False, mode=NOUN_MODE),
            # Target(word='fälschungssicher', fix='', lb=False, rb=False, cs=False, mode=NOUN_MODE),
            # Target(word='Rheuma', fix='', lb=False, rb=False, cs=False, mode=NOUN_MODE),
            # Target(word='synthetisieren', fix='', lb=False, rb=False, cs=True, mode=VERB_MODE),
            # Target(word='Gefäß', fix='', lb=False, rb=False, cs=False, mode=NOUN_MODE),



            ]

    if file_accessable(welt_aid_json_file): # get init article ids from last history
        with open(welt_aid_json_file, 'r', encoding='utf8') as fp:
            content = json.load(fp)
            for aid, _ in content.items():
                article_ids[aid] = 0
                path = f'{cache_folder}/{aid}.html'
                if file_accessable(path):
                    cached_article_ids.add(aid)
        print(f'load urls from history: {len(article_ids)}')
    if file_accessable(plus_aid_json_file): # get init article ids from last history
        with open(plus_aid_json_file, 'r', encoding='utf8') as fp:
            plus_spiegel_aids = json.load(fp)
        print(f'load plus urls from history: {len(plus_spiegel_aids)}')


    if len(targets) != 0:
        start_crawl(targets)

    zip_up_rst()
    delete_tmp_articles()

    with open(welt_aid_json_file, 'w+', encoding='utf8') as fp: # save article_ids
        json.dump(article_ids, fp)
    with open(plus_aid_json_file, 'w+', encoding='utf8') as fp: # save article_ids
        json.dump(plus_spiegel_aids, fp)

