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
from typing import Dict
from os import access, R_OK
from os.path import isfile
from pyquery import PyQuery as pq
from datetime import datetime
from functools import wraps


TIMEOUT = httpx.Timeout(360.0, connect=360.0)
PROXIES={ 'http': 'http://127.0.0.1:58591', 'https': 'http://127.0.0.1:58591', }
PROXY = 'http://127.0.0.1:58591'

ONE_DRIVE_PATH = 'C:\\Users\\fvdi0046\\OneDrive2\\OneDrive\\articles'
MAX_SLEEP_TIME = 300
logging.basicConfig(filename=ONE_DRIVE_PATH + '\\crawl_log.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    encoding='utf8',
                    level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.CRITICAL) # not let httpx logging

THREADS = 20
MAX_THREADS = 100

NOUN_MODE          = 1
VERB_MODE          = 2
SEP_VERB_MODE      = 3
PHRASE_MODE        = 4
COMPOUND_NOUN_MODE = 5
ADJECTIVE_MODE     = 6
VERB_PHRASE_MODE   = 7
OTHER_MODE         = 9
MANUAL_TARGETS     = 10


TARGET_CNT = 5 # default target cnt

article_ids = {}
cached_article_ids = set()
# die Welt
WELT_HOME_URL = 'https://www.welt.de'
WELT_AID_TYPE = 10
# der Spiegel
SPIEGEL_HOME_URL = 'https://www.spiegel.de'
plus_spiegel_aids = {}
SPIEGEL_AID_TYPE = 20
spiegel_aid_re = r'a-[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}'
spiegel_plus_hint = 'SPIEGEL+ wird über Ihren iTunes-Account abgewickelt und mit Kaufbestätigung bezahlt.'
# dw
DW_HOME_URL = 'https://www.dw.com/de'
DW_AID_TYPE = 30
dw_aid_re = r'a-\d{8}'

welt_aid_json_file = 'welt-aids.json'
plus_aid_json_file = 'plus-aids.json'

targets = []
history_words = []

folder_path = './articles'
cache_folder = './cache'
sentence_len = 40 # count by word

received_bytes = 0
cache_hit_cnt = 0
tm1 = time.perf_counter()

# a-d910b65e-6d6d-4358-a38e-84e525b0b5b6
manual_skip_list = {
        'a-0ed2413e-3872-4dab-8d2a-cbdc6ca0fa66',
        'a-25298a2a-9f51-41b9-9fa6-76f6b735cac6',
        'a-26bc6320-8efe-494a-9959-160f7b89e187',
        'a-6e0d2dcc-0002-0001-0000-000177967165',
        'a-b8720172-229d-43e9-8db2-73d1930e8f1b',
        'a-b4cd6f55-0002-0001-0000-000041784656', # too long
        'article5118821', # too long
        'article12073266',
        'article12605556',
        'article13528790', # too long
        'article13663598', # too long
        'article13903849', # too long
        'article116955753', # too long
        }

noun_skip_words = {
        '', '(dem)', '(den)', '(der)', '(des)', '(die)', '(ein)', '(eine)', '(einem)', '(einen)', '(einer)', '(eines)', '(keine)', '(keinen)', '(keiner)', 'am', 'das', 'dem', 'den', 'der', 'des', 'die', 'ein', 'eine', 'einem', 'einen', 'einer', 'eines', 'er', 'es', 'ist', 'keine', 'keinen', 'keiner', 'sie', 'sind', '—'
        }

verb_skip_words = {
        '-', 'bin', 'bist', 'habe', 'haben', 'habest', 'habet', 'habt', 'hast', 'hat', 'hatte', 'hatten', 'hattest', 'hattet', 'hätte', 'hätten', 'hättest', 'hättet', 'ist', 'sei', 'seid', 'seien', 'seiest', 'seiet', 'sein', 'sind', 'war', 'waren', 'warst', 'wart', 'werde', 'werden', 'werdet', 'wird', 'wirst', 'wäre', 'wären', 'wärest', 'wäret', 'würde', 'würden', 'würdest', 'würdet'
        }

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def cprint(color, content, end='\n'):
    print(color + content + bcolors.ENDC, end=end)

def file_accessable(path):
    if isfile(path) and access(path, R_OK):
        return True
    return False

def is_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def determine_url_by_aid(aid):
    if re.match(spiegel_aid_re, aid):
        return SPIEGEL_HOME_URL + '/' + aid
    if re.match(dw_aid_re, aid):
        return DW_HOME_URL + '/' + aid
    else:
        return WELT_HOME_URL + '/' + aid

def determine_type_by_aid(aid):
    if re.match(spiegel_aid_re, aid):
        return SPIEGEL_AID_TYPE
    if re.match(dw_aid_re, aid):
        return DW_AID_TYPE
    else:
        return WELT_AID_TYPE

def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        stime = time.perf_counter()
        result = func(*args, **kwargs)
        etime = time.perf_counter()
        elapse = etime - stime
        print(f'{func.__name__} used {elapse:.4f} second' + ' ' * 120)
        return result
    return timeit_wrapper

def _gaid(rst):
    _aid = rst[0]
    try:
        idx = _aid.index('#:')
        _aid = _aid[:idx]
        return _aid
    except:
        pass
    return _aid

def gaid(url): # get article id
    rst = re.findall(r"article\d+", url)
    if len(rst) > 0: return _gaid(rst)
    rst = re.findall(spiegel_aid_re, url)
    if len(rst) > 0: return _gaid(rst)
    rst = re.findall(dw_aid_re, url)
    if len(rst) > 0: return _gaid(rst)

    return None

def get_adj_declension(noun):
    rst = set()
    resp = requests.get(f'https://de.wiktionary.org/wiki/Flexion:{noun}')
    doc = pq(resp.content.decode('utf8'))
    tbl = doc('.inflection-table')
    tds = tbl('td')
    tmp = ''
    for td in tds.items():
        txt = str(td.text())
        tmp += (txt + ' ')

    for d in re.split(' |\n|,', tmp):
        if d.strip() in noun_skip_words:
            continue
        rst.add(d.strip())
    return rst

def rm_digits(word):
    return word.strip().replace('0', '').replace('1', '').replace('2', '').replace('3', '').replace('4', '').replace('5', '').replace('6', '').replace('7', '').replace('8', '').replace('9', '')

def get_declension2(noun):
    rst = set()
    resp = requests.get(f'https://en.wiktionary.org/wiki/{noun}')
    doc = pq(resp.content.decode('utf8'))
    tbl = doc('.inflection-table-de')
    tds = tbl('td')
    for td in tds.items():
        txt = str(td.text())
        if txt in noun_skip_words:
            continue
        if ',' in txt:
            for d in (d for d in txt.split(',')):
                to_add = rm_digits(d)
                if to_add not in noun_skip_words:
                    rst.add(to_add)
        else:
            to_add = rm_digits(txt)
            if to_add not in noun_skip_words:
                rst.add(to_add)
    return rst

def get_conjuncated(verb, prefix, mode):
    resp = requests.get('https://api.verbix.com/conjugator/iv1/6153a464-b4f0-11ed-9ece-ee3761609078/1/13/113/' + verb)
    content = json.loads(resp.content.decode('utf8'))

    doc = pq(content['p1']['html'])
    conjuncated = doc('span.normal')
    irregular = doc('span.irregular')
    verbs = {verb}
    for c in itertools.chain(conjuncated.items(), irregular.items()):
        for w in (w.strip().replace('(', '').replace(')', '') for w in str(c.text()).split(' ')):
            if prefix == '' or mode in (SEP_VERB_MODE, VERB_PHRASE_MODE):
                verbs.add(w)
            elif w.startswith(prefix) and len(w) > len(prefix):
                verbs.add(w)

    for discard_w in verb_skip_words:
        verbs.discard(discard_w)

    return verbs

class Result:
    def __init__(self, word):
        self.word = word
        self.rst_list = []
    def __hash__(self):
        return hash(self.word)
    def __eq__(self, other):
        if not isinstance(other, Result):
            return NotImplemented
        return self.word == other.word

    def add_candidate(self, aid, purity, prompt):
        """
        purity: count of learned word in sentence(s) / count of all words in sentence(s)
        prompt: write to file
        """
        self.rst_list.append({'aid': aid, 'purity': purity, 'prompt': prompt})

    def write_results(self):
        for rst in sorted(self.rst_list, key=lambda x : x['purity'], reverse=True)[:5]:
            purity, aid = rst['purity'], rst['aid']
            logging.info(f'writing `{self.word}` result of purity {purity:0.4f} in {aid}')
            fname = f'./{folder_path}/article-{self.word}-' + rst['aid'] + '.txt'
            fname = unicodedata.normalize('NFD', fname.replace('ß', 'ss')).encode('ascii', 'ignore').decode('utf8')
            with open(fname, 'w+', encoding='utf8') as f:
                f.write(rst['prompt'])

results : Dict[str, Result]

class Target:
    def __init__(self, word:str, mode, lb=False, rb=False, cs=False, target_cnt=TARGET_CNT, prefix='', suffix=''):
        self.key_noun_verb = word # noun or verb
        self.lborder = lb # left border
        self.rborder = rb # right border
        self.case_sensitive = cs
        self.match_mode = mode
        self.hit_urls = set()
        self.target_cnt = target_cnt
        self.prefix = prefix
        self.suffix = suffix
        self.completed = False
        self.true_noun = False
        if mode in (VERB_MODE, SEP_VERB_MODE, VERB_PHRASE_MODE):
            self.conjuncated = get_conjuncated(self.key_noun_verb, self.prefix, self.match_mode)
            if len(self.conjuncated) == 0:
                cprint(bcolors.FAIL, f'can not conjuncate:{self.key_noun_verb}')
                exit(1)
            print(f'verb target: {", ".join(t for t in self.conjuncated)}')
        if mode == NOUN_MODE and self.key_noun_verb[0].isupper():
            self.true_noun = True
            self.declensions = get_declension2(self.key_noun_verb)
            if len(self.declensions) == 0:
                cprint(bcolors.FAIL, f'can not declension:{self.key_noun_verb}')
                self.true_noun = False
            else:
                print(f'noun target: {", ".join(dkl for dkl in self.declensions)}')
        if mode == COMPOUND_NOUN_MODE and self.key_noun_verb[0].isupper():
            self.true_noun = True
            declensions = get_declension2(self.key_noun_verb)
            if len(declensions) == 0:
                cprint(bcolors.FAIL, f'can not declension:{self.key_noun_verb}')
                self.true_noun = False
                self.key_noun_verb = self.prefix + self.key_noun_verb
            else: # compound noun and prefix
                c_dkl = {self.prefix + dkl.lower() for dkl in declensions}
                self.declensions = c_dkl
                print(f'noun target: {", ".join(dkl for dkl in self.declensions)}')
        if mode == ADJECTIVE_MODE:
            declensions = get_adj_declension(self.key_noun_verb)
            if len(declensions) == 0:
                cprint(bcolors.FAIL, f'can not declension:{self.key_noun_verb}')
                self.declensions = []
            else:
                self.declensions = declensions if self.prefix == '' else [self.prefix + d for d in declensions]
                print(f'adjective target: {", ".join(dkl for dkl in self.declensions)}')

    def __str__(self):
        s = []
        if self.prefix: s.append('prefix = ' + self.prefix)
        s.append('word = ' + self.key_noun_verb)
        if self.suffix: s.append('suffix = ' + self.suffix)
        if self.lborder: s.append('left-border')
        if self.rborder: s.append('right-border')
        if self.case_sensitive: s.append('case-sensitive')
        s.append(f'target cnt = {self.target_cnt}')

        if self.match_mode == NOUN_MODE: s.append(f'NOUN_MODE')
        if self.match_mode == VERB_MODE: s.append(f'VERB_MODE')
        if self.match_mode == SEP_VERB_MODE: s.append(f'SEP_VERB_MODE')
        if self.match_mode == PHRASE_MODE: s.append(f'PHRASE_MODE')
        if self.match_mode == COMPOUND_NOUN_MODE: s.append(f'COMPOUND_NOUN_MODE')
        if self.match_mode == ADJECTIVE_MODE: s.append(f'ADJECTIVE_MODE')
        if self.match_mode == VERB_PHRASE_MODE: s.append(f'VERB_PHRASE_MODE')
        if self.match_mode == OTHER_MODE: s.append(f'OTHER_MODE')
        if self.match_mode == MANUAL_TARGETS: s.append(f'MANUAL_TARGETS')
        return ', '.join(s)

    def wrap_border(self, noun):
        pattern = noun.lower() if not self.case_sensitive else noun
        if self.lborder:
            pattern = r"\b" + pattern
        if self.rborder:
            pattern = pattern + r"\b"
        return pattern

    def search(self, pat, content):
        sentences = content.split('.')
        for sentence in sentences:
            if len(sentence.split(' ')) > sentence_len:
                continue
            if self.case_sensitive and re.search(pat, content):
                return True
            elif not self.case_sensitive and re.search(pat, content, re.IGNORECASE):
                return True
        return False

    def calc_purity_params(self, paragraph):
        word_len, hist_word_len = len(paragraph.split(' ')), 0
        for w in history_words:
            if w in paragraph:
                hist_word_len += 1
        return (hist_word_len, word_len)
        

    def hit(self, paragraph):
        if self.match_mode == NOUN_MODE or self.match_mode == COMPOUND_NOUN_MODE:
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
        if self.match_mode == ADJECTIVE_MODE:
            for dkl in self.declensions:
                pattern = self.wrap_border(dkl)
                if self.search(pattern, paragraph):
                    return True
            pattern = self.wrap_border(self.key_noun_verb)
            if self.search(pattern, paragraph):
                return True
            return False

        if self.match_mode == VERB_MODE:
            for kw in self.conjuncated:
                pattern = r"\b" + kw.lower() + r"\b"
                if self.search(pattern, paragraph):
                    return True
            return False
        if self.match_mode == SEP_VERB_MODE:
            for kw in self.conjuncated:
                pattern = r"\b" + kw.lower() + r"\b[^\.:,]*\b" + self.prefix + r"[^a-zA-Z0-9] "
                if self.search(pattern, paragraph):
                    return True
            for kw in self.conjuncated:
                pattern = r"\b" + self.prefix + kw.lower() + r"\b"
                if self.search(pattern, paragraph): return True
                pattern = r"\b" + self.prefix + 'zu' + kw.lower() + r"\b"
                if self.search(pattern, paragraph): return True
            return False
        if self.match_mode == PHRASE_MODE:
            pattern = r"\b" + self.prefix + r"\b[^\.]*\b" + self.key_noun_verb + r"\b"
            if self.suffix != '':
                pattern += (r"\b[^\.]*\b" + self.suffix)
            if self.search(pattern, paragraph):
                return True
            return False
        if self.match_mode == VERB_PHRASE_MODE:
            for kw in self.conjuncated:
                pattern = r"\b" + self.prefix + r"\b[^\.]*\b" + kw + r"\b" + (r"\b[^\.]*\b" + self.suffix if self.suffix != '' else '')
                if self.search(pattern, paragraph):
                    return True
            return False

    def get_kw(self) -> str:
        kw = self.key_noun_verb
        if self.match_mode == VERB_MODE:
            kw = self.key_noun_verb
        if self.match_mode == SEP_VERB_MODE:
            kw = self.prefix + self.key_noun_verb
        if self.match_mode in (PHRASE_MODE, VERB_PHRASE_MODE):
            kw = self.prefix + '...' + self.key_noun_verb + ('...' + self.suffix if self.suffix != '' else '')
        if self.match_mode == COMPOUND_NOUN_MODE:
            kw = self.prefix + self.key_noun_verb.lower()
        if self.match_mode == ADJECTIVE_MODE and self.prefix != '':
            kw = self.prefix + self.key_noun_verb.lower()
        return kw

    def generate_prompt(self, hit_paras:list):
        idx = 1
        prompt = f'对于下面这篇德语文章\n'
        # prompt += f'{idx}.打印出‘{kw}’的音标(包括重音符号)'; idx += 1

        prompt += f'{idx}.为这篇德语文章生成一篇简短的中文摘要并提取5个关键词(逗号分隔)\n'; idx += 1
        for hp in hit_paras:
            prompt += f'{idx}.打印原文第{hp}段\n'; idx += 1
            prompt += f'{idx}.翻译第{hp}段成中文\n'; idx += 1
            prompt += f'{idx}.翻译第{hp}段成日语\n'; idx += 1
            prompt += f'{idx}.翻译第{hp}段成英语\n'; idx += 1

        return prompt

def process_hit(target:Target, aid, url, paragraph_contents, hit_paragraph_nos, purity=0.0):
    # print(f'hit {target.get_kw()} in {aid} of purity {purity:0.4f}' + (' ' * 100))
    global results
    result = results.get(target.get_kw())
    if result is not None:
        prompt = target.generate_prompt([str(p) for p in sorted(hit_paragraph_nos)]) + '\n'
        for i, p in enumerate(paragraph_contents, start=1):
            prompt += f'p{i}:\n'
            prompt += f'{p}\n'
        result.add_candidate(aid, purity, prompt)

    target.hit_urls.add(url)
    if target.target_cnt == len(target.hit_urls):
        cprint(bcolors.OKGREEN, f'{target.get_kw()} complete! at {datetime.now().strftime("%m/%d/%Y %H:%M:%S")}' + (' ' * 100))
        logging.info(f'{target.get_kw()} complete!')
        target.completed = True

def parse_txt_article(aid):
    global targets
    progress_bar(targets)
    url = determine_url_by_aid(aid)
    fp = f'{cache_folder}/{aid}.txt'
    a_content = []
    with open(fp, 'r', encoding='utf8') as f:
        a_content = [line.strip() for line in f]
    for target in targets:
        if url in target.hit_urls: continue
        hit_flag, hit_paragraph_nos = False, set()
        total_word_len, hist_word_len = 0, 0

        for i, p in enumerate(a_content, start=1):
            if p.startswith(spiegel_plus_hint):
                plus_spiegel_aids[aid] = 1
                return
            if target.hit(p):
                hit_flag = True
                hit_paragraph_nos.add(i)
                # calculate purity
                _hist_word_len, _word_len = target.calc_purity_params(p.lower())
                total_word_len += _word_len
                hist_word_len += _hist_word_len
        if hit_flag and url not in target.hit_urls:
            print(f'hit {target.get_kw()} of purity {hist_word_len}/{total_word_len}' + (' ' * 100))
            process_hit(target, aid, url, a_content, hit_paragraph_nos, purity=(float(hist_word_len)/float(total_word_len)))
    article_ids[aid] = 1 # marked as searched
    progress_bar(targets)

def write_paragraphs(aid, fp, paragraphs:list):
    with open(fp, 'w+', encoding='utf8') as f:
        for _, p in enumerate((p.strip() for p in paragraphs if p.strip() != ''), start=1):
            f.write(p + '\n')
    if file_accessable(f'{cache_folder}/{aid}.html'):
        os.unlink(f'{cache_folder}/{aid}.html')
    parse_txt_article(aid)

def parse_welt_article(content, aid):
    doc = pq(content)
    page = doc('.c-article-page__container')
    paragraphs = page('p')
    paras = [str(p.text()) for p in paragraphs.items()]
    write_paragraphs(aid, f'{cache_folder}/{aid}.txt', paras)

def parse_spiegel_article(content, aid):
    global spiegel_plus_hint
    if aid in plus_spiegel_aids: return
    doc = pq(content)
    paragraphs = doc('p')
    title = [str(doc('#Inhalt > article > header').text())]
    title.extend([str(p.text()) for p in paragraphs.items()])
    write_paragraphs(aid, f'{cache_folder}/{aid}.txt', title)

def parse_dw_article(content, aid):
    doc = pq(content)
    content = doc('article')
    paragraphs = doc('p')
    title = [str(content('header > h1').text())]
    title.extend([str(p.text()) for p in paragraphs.items()])
    write_paragraphs(aid, f'{cache_folder}/{aid}.txt', title)

def parse_article(content, aid):
    global targets
    recruit_from_content(content)
    type = determine_type_by_aid(aid)
    if type == WELT_AID_TYPE:
        parse_welt_article(content, aid)
    if type == SPIEGEL_AID_TYPE:
        parse_spiegel_article(content, aid)
    if type == DW_AID_TYPE:
        parse_dw_article(content, aid)

    article_ids[aid] = 1 # marked as searched
    # recruit other links
    progress_bar(targets)

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
    path1 = f'{cache_folder}/{aid}.txt'
    path = f'{cache_folder}/{aid}.html'
    progress_bar(targets)
    if file_accessable(path1):
        cache_hit_cnt += 1
        parse_txt_article(aid)
    elif file_accessable(path):
        cache_hit_cnt += 1
        async with aiofiles.open(path, mode='r', encoding='utf8') as f:
            async for l in f:
                content += l
        parse_article(content, aid)
    else:
        url = determine_url_by_aid(aid)
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            try:
                resp = await client.get(url=url)
                content = resp.content.decode('utf8')
            except:
                logging.info(f'error in request: {url}')
                return aid
            received_bytes += len(content)
            with open(path, 'w+', encoding='utf8') as fw:
                fw.write(content)
        parse_article(content, aid)
    return aid


async def launch(async_fun, params):
    aids = await asyncio.gather(*map(async_fun, params))
    return aids

def urls_info(flg): # 1 searched; 0 remain
    global article_ids
    return len(([k for k, v in article_ids.items() if v == flg]))

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

def collect_markdowns():
    global folder_path
    # delete md- files
    for filename in os.listdir(folder_path):
        if not filename.startswith('md-') or not filename.endswith('.md'):
            continue
        file_path = os.path.join(folder_path, filename)
        delete_file(file_path)
    # file key words
    keywords = set()
    for filename in os.listdir(folder_path):
        if not filename.startswith('article-') or not filename.endswith('.md'):
            continue
        kw = filename.split('-')[1]
        keywords.add(kw)
    for k in keywords:
        with open(f'{folder_path}/md-{k}.md', mode='w+', encoding='utf8') as mkf:
            for filename in os.listdir(folder_path):
                if not filename.startswith('article-') or not filename.endswith('.md') or k not in filename:
                    continue
                mkf.write('\n\n')
                mkf.write('> =======================================================================<br>\n')
                mkf.write('> ===============================NEW PAGE=================================<br>\n')
                mkf.write('> =======================================================================<br>\n')
                mkf.write('\n')

                with open(f'{folder_path}/{filename}', mode='r', encoding='utf8') as rf:
                    content = ''
                    for ln in rf:
                        # add one space in `**` for markdown bold display properly
                        bold_mark_idxs = [m.start() for m in re.finditer(r'\*\*', ln)]
                        for i, idx in enumerate(reversed(bold_mark_idxs), start=1):
                            split_idx = idx + 2 if i % 2 == 1 else idx
                            ln = ln[:split_idx] + ' ' + ln[split_idx:]
                        content += f'{ln.rstrip()}\n'
                    # content = content.replace('---', '')
                    mkf.write(content)
    # zip up
    target_zip = f'/md_archive{datetime.now().strftime("%Y%m%d-%H%M%S")}.zip'
    with zipfile.ZipFile(folder_path + target_zip, 'w') as zipf:
        for filename in os.listdir(folder_path):
            if not filename.startswith('md-') or not filename.endswith('.md'):
                continue
            file_path = os.path.join(folder_path, filename)
            zipf.write(file_path)
    shutil.copyfile(f'{folder_path}/{target_zip}', f'{folder_path}/md_archive.zip')


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
    incomplete = [t for t in targets if not t.completed]
    ptargets = incomplete if len(incomplete) <= 30 else incomplete[:30]
    for i, t in enumerate(ptargets, start=1):
        if i != 1:
            s += '|'
        # s += ('〇' if t.completed else str(t.target_cnt - len(t.hit_urls)))
        s += str(t.target_cnt - len(t.hit_urls))
    bl = readable_byte_len(received_bytes)
    progress = f'[{s}] {urls_info(1)} searched, {urls_info(0)} remain {tm2-tm1:0.2f} sec {bl} received'
    # progress += f' {datetime.now().strftime("%m/%d/%Y %H:%M:%S")}'
    print(f'{progress}\r', end='')

def recruit_from_url(url):
    global article_ids, received_bytes
    before = len(article_ids)
    response = requests.get(url)
    # print(f'{url} : {response.status_code}')
    received_bytes += len(response.content)
    recruit_from_content(response.content)
    recruited = len(article_ids) - before
    print(f'recruit {recruited} from {url}')

def startwith_home(url):
    if url.startswith(WELT_HOME_URL): return True
    if url.startswith(SPIEGEL_HOME_URL): return True
    if url.startswith(DW_HOME_URL): return True
    return False

def recruit_from_content(content):
    doc = pq(content)
    anchors = doc('a')
    for a in anchors:
        if 'href' not in a.attrib:
            continue
        ref = a.attrib['href']
        _aid = gaid(ref)
        if ((len(ref) > 0 and ref[0] == '/') or startwith_home(ref)) and _aid and _aid not in article_ids:
            article_ids[_aid] = 0 # recruit url

def unsearched(aid):
    if aid not in article_ids:
        return True
    if article_ids[aid] == 0:
        return True
    return False

@timeit
def recruit_from_home():
    recruit_from_url(WELT_HOME_URL)
    recruit_from_url(SPIEGEL_HOME_URL)
    recruit_from_url(DW_HOME_URL)

def print_aid_summary():
    global article_ids, cached_article_ids
    total, welt, spiegel, dw = 0, 0, 0, 0
    for aid in article_ids.keys():
        total += 1
        type = determine_type_by_aid(aid)
        if type == WELT_AID_TYPE: welt += 1
        if type == SPIEGEL_AID_TYPE: spiegel += 1
        if type == DW_AID_TYPE: dw += 1
    cprint(bcolors.OKGREEN, f'links: ')
    cprint(bcolors.OKGREEN, f'welt: {welt}({welt * 100 / total:.2f}%)', end=', ')
    cprint(bcolors.OKGREEN, f'spiegel: {spiegel}({spiegel * 100 / total:.2f}%)', end=', ')
    cprint(bcolors.OKGREEN, f'dw: {dw}({dw * 100 / total:.2f}%)', end='\n')
    total, welt, spiegel, dw = 0, 0, 0, 0
    for aid in cached_article_ids:
        total += 1
        type = determine_type_by_aid(aid)
        if type == WELT_AID_TYPE: welt += 1
        if type == SPIEGEL_AID_TYPE: spiegel += 1
        if type == DW_AID_TYPE: dw += 1
    cprint(bcolors.OKCYAN, f'cached: ')
    cprint(bcolors.OKCYAN, f'welt: {welt}({welt * 100 / total:.2f}%)', end=', ')
    cprint(bcolors.OKCYAN, f'spiegel: {spiegel}({spiegel * 100 / total:.2f}%)', end=', ')
    cprint(bcolors.OKCYAN, f'dw: {dw}({dw * 100 / total:.2f}%)', end='\n')

# @timeit
def sampling_aids():
    uncached = (k for k, _ in article_ids.items() if unsearched(k) and k not in cached_article_ids and k not in plus_spiegel_aids)
    aids1 = list(itertools.islice((k for k in uncached if random.randint(0, 1) == 1), THREADS))
    aids_cached = list(itertools.islice((k for k in cached_article_ids if unsearched(k) and random.randint(0, 1) == 1), MAX_THREADS))

    # expand spiegel and dw
    aids_spiegel = (k for k, _ in article_ids.items() if determine_type_by_aid(k) == SPIEGEL_AID_TYPE and k not in plus_spiegel_aids and k not in cached_article_ids and unsearched(k))
    aids_spiegel = list(itertools.islice((k for k in aids_spiegel if random.randint(0, 1) == 1), 10))
    aids_dw = (k for k in article_ids.keys() if determine_type_by_aid(k) == DW_AID_TYPE and unsearched(k) and k not in cached_article_ids)
    aids_dw = list(itertools.islice((k for k in aids_dw if random.randint(0, 1) == 1), 10))

    aids = [aid for aid in (aids1 + aids_cached + aids_spiegel + aids_dw) if unsearched(aid)]
    return aids

@timeit
def crawl(targets, delete_tmp=True, least_run_circle=15):
    global results, history_words
    recruit_from_home()
    if delete_tmp:
        delete_tmp_articles()
    with open(ONE_DRIVE_PATH + '\\history.txt', 'r', encoding='utf8') as f:
        history_words = f.read().splitlines()

    circles = 0
    while (not all(t.completed for t in targets) and urls_info(0) > THREADS and not file_accessable('./stop.txt')) or circles < least_run_circle:
        circles += 1
        if file_accessable(ONE_DRIVE_PATH + '\\stop.txt'):
            break
        aids = sampling_aids()

        atm1 = time.perf_counter()
        done_aids = asyncio.run(launch(get_content_and_parse, aids))
        for aid in done_aids:
            article_ids[aid] = 1
        atm2 = time.perf_counter()
        print(f'ascyn run used {atm2-atm1:.2f} sec for {len(done_aids)} articles' + ' ' * 100)

        progress_bar(targets)

    for r in results.values():
        r.write_results()

    print(f'\n{urls_info(1)} article searched', end='\n')
    bl = readable_byte_len(received_bytes)
    print(f'{bl} data received')
    if urls_info(1) != 0:
        cprint(bcolors.OKCYAN, f'{cache_hit_cnt} cache hit ({float(cache_hit_cnt * 100)/urls_info(1):.2f}%)')
    # print incomplete target(s)
    for t in targets:
        if not t.completed:
            print(t.get_kw(), 'not completed', end='\n')
    zip_up_rst()
    # delete_tmp_articles()

@timeit
def load_history_and_summary():
    cprint(bcolors.HEADER, 'start loading history...')
    if file_accessable(welt_aid_json_file): # get init article ids from last history
        with open(welt_aid_json_file, 'r', encoding='utf8') as fp:
            content = json.load(fp)
            _tmp_fn = set()
            for filename in os.listdir(cache_folder):
                _tmp_fn.add(filename)
            for aid, _ in content.items():
                article_ids[aid] = 0
                if f'{aid}.html' in _tmp_fn or f'{aid}.txt' in _tmp_fn:
                    cached_article_ids.add(aid)
        print(f'load urls from history: {len(article_ids)}')
    if file_accessable(plus_aid_json_file): # get init article ids from last history
        with open(plus_aid_json_file, 'r', encoding='utf8') as fp:
            plus_spiegel_aids = json.load(fp)
        print(f'load plus urls from history: {len(plus_spiegel_aids)}')
    print_aid_summary()

@timeit
def save_history():
    with open(welt_aid_json_file, 'w+', encoding='utf8') as fp: # save article_ids
        json.dump(article_ids, fp)
    with open(plus_aid_json_file, 'w+', encoding='utf8') as fp: # save article_ids
        json.dump(plus_spiegel_aids, fp)

def start_sentry():
    global targets, results
    sleep_time = 2
    while True:
        print(f'sleep for {sleep_time} sec at {datetime.now().strftime("%m/%d/%Y %H:%M:%S")}\r', end='')
        time.sleep(sleep_time)
        sleep_time = sleep_time + 10 if sleep_time + 10 < MAX_SLEEP_TIME else MAX_SLEEP_TIME
        if not file_accessable(ONE_DRIVE_PATH + '\\targets.txt'): continue
        # print('file accessable')
        with open(ONE_DRIVE_PATH + '\\targets.txt', 'r', encoding='utf8') as f:
            content = f.read().splitlines()
        if len(content) <= 1: continue
        print('file has content')
        first_ln = content[0]
        if first_ln.strip() != 'RUN':
            continue
        logging.info('accept RUN instruction')
        targets, results = [], {} # init targets and results

        for ln in content[1:]: # first word should be target
            if len(ln.strip()) == 0: continue # skip empty line
            words = ln.split()
            prefix, word, mode, lb, rb, cs, tc = '', '', NOUN_MODE, False, False, False, TARGET_CNT

            for w in words:
                if w == 'N': mode = NOUN_MODE
                if w == 'S': mode = SEP_VERB_MODE
                if w == 'V': mode = VERB_MODE
                if w == 'C': mode = COMPOUND_NOUN_MODE
                if w == 'A': mode = ADJECTIVE_MODE
                if w == 'l': lb = True
                if w == 'r': rb = True
                if w == 'c': cs = True
                if is_integer(w): tc = int(w)
            if mode == COMPOUND_NOUN_MODE or mode == SEP_VERB_MODE:
                prefix, word = words[0], words[1]
            else:
                word = words[0]
            t = Target(prefix=prefix, word=word, lb=lb, rb=rb, cs=cs, mode=mode, target_cnt=tc)
            logging.info(f'Target: {t}')
            targets.append(t)
            r = Result(t.get_kw())
            results[t.get_kw()] = r

        if len(targets) != 0:
            logging.info('sentry active!')
            # load_history_and_summary()
            crawl(targets , True) # sentry do not clear result
            save_history()
            shutil.copyfile(f'{ONE_DRIVE_PATH}\\targets.txt', f'{ONE_DRIVE_PATH}\\targets-bak.txt')
            with open(f'{ONE_DRIVE_PATH}\\targets.txt', 'w+', encoding='utf8') as f:
                f.write('DONE!')
            logging.info('sentry sleep')


if __name__ == '__main__':

    targets = [ ]

    load_history_and_summary()

    # if len(targets) != 0:
    #     crawl(targets , True)
    #     save_history()

    # collect_markdowns()

    start_sentry()
