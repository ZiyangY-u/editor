#!/usr/bin/python3

# completion_buf.db schema:

# drop table words;
# drop table path_history;
# create table words (word text, chosen int, src, recent_chosen_time datetime, import_date datetime, occur_cnt int not null,inc_a int,inc_b int,inc_c int,inc_d int,inc_e int,inc_f int,inc_g int,inc_h int,inc_i int,inc_j int,inc_k int,inc_l int,inc_m int,inc_n int,inc_o int,inc_p int,inc_q int,inc_r int,inc_s int,inc_t int,inc_u int,inc_v int,inc_w int,inc_x int,inc_y int,inc_z int);
# create index idx_words on words(word, chosen);
# create index idx_words_src on words(src);
# create index idx_words_occur on words(occur_cnt);
# create index idx_words_a on words(inc_a);
# create index idx_words_b on words(inc_b);
# create index idx_words_c on words(inc_c);
# create index idx_words_d on words(inc_d);
# create index idx_words_e on words(inc_e);
# create index idx_words_f on words(inc_f);
# create index idx_words_g on words(inc_g);
# create index idx_words_h on words(inc_h);
# create index idx_words_i on words(inc_i);
# create index idx_words_j on words(inc_j);
# create index idx_words_k on words(inc_k);
# create index idx_words_l on words(inc_l);
# create index idx_words_m on words(inc_m);
# create index idx_words_n on words(inc_n);
# create index idx_words_o on words(inc_o);
# create index idx_words_p on words(inc_p);
# create index idx_words_q on words(inc_q);
# create index idx_words_r on words(inc_r);
# create index idx_words_s on words(inc_s);
# create index idx_words_t on words(inc_t);
# create index idx_words_u on words(inc_u);
# create index idx_words_v on words(inc_v);
# create index idx_words_w on words(inc_w);
# create index idx_words_x on words(inc_x);
# create index idx_words_y on words(inc_y);
# create index idx_words_z on words(inc_z);
# create table path_history (path text, hash text, import_date datetime);
# create index idx_path_history on path_history(path, hash);

import sys
import re
import sqlite3
import logging
import copy
import subprocess
from os import access, R_OK
from os.path import isfile
from jpn_ime_service import HIRAKANA
from anon_expand import ESCAPE

COMPLETE_BUF_DB_PATH = '/root/.config/nvim/completion_buf.db'
JP_DICT_DB_PATH = '/root/.config/nvim/jp/completion.db'
CN_DICT_DB_PATH = '/root/.config/nvim/cn/completion.db'
WORD_PAT = re.compile('(?u)([\w]{3,})')
VOWELS = 'aeiou'
DELIMITATOR = '/'

TOTAL_CANDIDATES_ORDER_MODE = 4
NORMAL_ORDER = 0
RECENT_RECRUIT_ORDER = 1
WORD_LEN_ORDER = 2
MOST_CHOSEN_ORDER = 3

DIGITS = { '0': '０', '1': '１', '2': '２', '3': '３', '4': '４', '5': '５', '6': '６', '7': '７', '8': '８', '9': '９', ',': '，', }

GOBI = {
        # 動詞形
        'tte':'って',
        'tta':'った',
        'ite':'いて',
        'ita':'いた',
        'nde':'んで',
        'nda':'んだ',
        'nai':'ない',
        'shite':'して',
        'shita':'した',
        'masu':'ます',
        'mashi':'まし',
        'masen':'ません',
        'masenn':'ません',
        'nasai':'なさい',
        'desu':'です',
        'deshita':'でした',
        'reba':'れば',

        # 別の動詞
        'age':'あげ',
        'deki':'でき',
        'ike':'いけ',
        'shima':'しま',
        'sare':'され',
        'mi':'み',
        'kure':'くれ',
        'itada':'いただ',
        'mora':'もら',
        'na':'な', # なる、なり、ない
        'kudasai':'ください',
        'deki':'でき',

        # 単なる語尾
        'nara':'なら',
        'sou':'そう',
        'tara':'たら',

        # 単なる仮名
        'u':'う',
        'i':'い',
        'shi':'し',
        'zu':'ず',
        'ri':'り',
        're':'れ',
        'ke':'け',
        'de':'で',
        'ra':'ら',
        'se':'せ',
        'ba':'ば',
        'te':'て',
        'ku':'く',
        'ru':'る',
        'ta':'た',

        # 助詞
        'wo':'を',
        'ha':'は',
        'ga':'が',
        'to':'と',
        'de':'で',
        'ni':'に',
        'no':'の',
        'ka':'か',
        'darou':'だろう',
        'deshou':'でしょう',

        }

# logging.basicConfig(filename='./example.log', level=logging.DEBUG)

class CompletionItem:
    __slots__ = (
            "word" # completion word
            , "indicator"
            , "freq" # frequency
            , "sort"
            )

    def __init__(self, word, indicator, freq=0):
        self.word = word
        self.indicator = indicator
        self.freq = freq
    def __str__(self):
        return f"{self.word} {self.indicator}"

def query(sql:str, indicate:str, connection:sqlite3.Connection, rst:list) -> None:
    """
    query from completion db and print result
    :param sql: sql for query [word, frequency, chosen]
    :param indicate: indicator print after every result
    :param use_dict: use Japanese dictionary if True
    """
    cur = connection.cursor()
    cur.execute(sql)
    for item in cur.fetchall():
        rst.append(CompletionItem(item[0], indicate, float(item[1]) + float(item[2])))

def query_with_decor(sql:str, indicate:str, connection:sqlite3.Connection, tail_decor:str, rst:list) -> None:
    """
    query from completion db and add decoration in tail of every result
    :param sql: sql for query
    :param indicate: indicator print after every result
    :param use_dict: use Japanese dictionary if True
    :param tail_decor: tail decoration
    """
    cur = connection.cursor()
    cur.execute(sql)
    for item in cur.fetchall():
        rst.append(CompletionItem(item[0] + tail_decor, indicate, float(item[1]) + float(item[2])))

def query_and_inflect(sql:str, indicate:str, patch:str, tail_decor:str, connection:sqlite3.Connection, rst:list):
    cur = connection.cursor()
    cur.execute(sql)
    # logging.debug(sql)
    for item in cur.fetchall():
        rst.append(CompletionItem(item[0][:-1] + patch + tail_decor, indicate, float(item[1]) + float(item[2])))

def create_insert_word_sql(word:str, path:str, chosen:bool) -> str:
    # word text, chosen int, src, recent_chosen_time datetime, import_date
    chars = set([c.lower() for c in word if re.match("[A-Za-z]", c)])
    sql = 'insert into words (word, chosen, occur_cnt, src, recent_chosen_time, import_date'
    if len(chars) == 0:
        sql =  sql + ') values ("{}", 0, 0, "{}", {}, datetime("now"))'.format(word, path, 'null' if not chosen else 'datetime("now")')
    else:
        sql = sql + ',' + ','.join('inc_'+c for c in chars) + ') values ("{}", 0, 0, "{}", {}, datetime("now"),'.format(word, path, 'null' if not chosen else 'datetime("now")') \
                + ','.join('1' for _ in chars) + ')'
    return sql



def add_word(word:str, path:str) -> None:
    """
    add word to words table.
    :param word: word to add
    :param path: word source path
    """
    con_completion = sqlite3.connect(COMPLETE_BUF_DB_PATH)
    cur = con_completion.cursor()
    cur.execute(f"select count(1) from words where word = '{word}'")
    cnt = cur.fetchall()[0][0]
    if cnt == 0:
        cur.execute(create_insert_word_sql(word, path, True))
    else: # add occur_cnt
        cur.execute(f"update words set occur_cnt = occur_cnt + 1 where word = '{word}'")

    con_completion.commit()

def has_path_history(path:str, hashcode:str) -> bool:
    """
    return True if has history, False if no history.
    :param path: target file path
    :param hashcode: file's hash code
    """
    con_completion = sqlite3.connect(COMPLETE_BUF_DB_PATH)
    cur = con_completion.cursor()
    cur.execute(f"select count(1) from path_history where path = '{path}' and hash = '{hashcode}'")
    cnt = cur.fetchall()[0][0]
    return cnt != 0

def add_words(path:str, enc:str) -> None:
    """
    retrieve words from file and add to complition db
    Parameters
    ==========
    path: target file path
    enc: file encoding
    Returns
    ==========
    None
    """
    global words
    if not isfile(path) or not access(path, R_OK) or path.endswith('.log'):
        return
    result = subprocess.run(['sha1sum', path], stdout=subprocess.PIPE)
    hashcode = result.stdout.decode('utf8').split(' ')[0]
    if has_path_history(path, hashcode):
        return
    with open(path, encoding=enc) as f:
        tmp = set()
        try:
            tmp = set(re.findall(WORD_PAT, f.read()))
        except UnicodeDecodeError:
            with open(path, encoding='cp932'):
                tmp = set(re.findall(WORD_PAT, f.read()))
        con_completion = sqlite3.connect(COMPLETE_BUF_DB_PATH)
        cur = con_completion.cursor()
        for w in tmp:
            if not w.isascii():
                continue
            cur.execute(f"select count(1) from words where word = '{w}'")
            cnt = cur.fetchall()[0][0]
            if cnt == 0:
                cur.execute(create_insert_word_sql(w, path, False))
            else: # add occur_cnt
                cur.execute(f"update words set occur_cnt = occur_cnt + 1 where word = '{w}'")
        cur.execute('insert into path_history values ("' + path + '", "' + hashcode + '", datetime("now"))') # add path to history
    # clear not chosen words imported 1 days ago
    # and they will be recruited next time the file involved
    cur.execute('delete from words where chosen = 0 and import_date < datetime("now", "-1 day")')
    cur.execute('delete from words where chosen < 5 and recent_chosen_time < datetime("now", "-7 day")')
    cur.execute('delete from path_history where import_date < datetime("now", "-1 day")')
    con_completion.commit()


def query_word(word:str, src:str, order_mode:int) -> list:
    """
    get candidates from word complition
    :param word: word to query
    :param src: source path indication
    """
    rst_list = []
    con_completion = sqlite3.connect(COMPLETE_BUF_DB_PATH)
    # create like pattern: query -> %q%u%e%r%y%
    like_pat = '"%' + '%'.join((ch for ch in word)) + '%"'
    chars = set([c.lower() for c in word if re.match("[A-Za-z]", c)])
    # if all(re.match("[a-z]", c) for c in word):
    #     like_pat += ' COLLATE NOCASE  '
    and_pat = ' AND ' + ' AND '.join('inc_' + c + '=1' for c in chars)
    order_clause = ' ORDER BY RECENT_CHOSEN_TIME DESC, CHOSEN, OCCUR_CNT DESC'
    if order_mode == RECENT_RECRUIT_ORDER:
        order_clause = ' ORDER BY IMPORT_DATE DESC, LENGTH(WORD), OCCUR_CNT ASC'
    if order_mode == WORD_LEN_ORDER:
        order_clause = ' ORDER BY LENGTH(WORD) ASC, CHOSEN DESC, RECENT_CHOSEN_TIME, OCCUR_CNT DESC'
    if order_mode == MOST_CHOSEN_ORDER:
        order_clause = ' ORDER BY CHOSEN DESC, LENGTH(WORD) ASC, RECENT_CHOSEN_TIME, OCCUR_CNT DESC'
    # chosen history
    sql = 'SELECT DISTINCT WORD, 0, CHOSEN FROM WORDS WHERE LENGTH(WORD) < 100 AND WORD LIKE ' + like_pat + and_pat + order_clause
    query(sql, '󱈅 word', con_completion, rst_list)

    return rst_list

def choose(word:str) -> None:
    """
    add chosen :param word: count in complition db.
    if word not exists add it
    """
    con_completion = sqlite3.connect(COMPLETE_BUF_DB_PATH)
    cur = con_completion.cursor()
    cur.execute(f"select chosen from words where word = '{word}' limit 1")
    chosen_cnt = cur.fetchall()
    if len(chosen_cnt) == 1:
        cnt = chosen_cnt[0][0] + 1
        sql = f"update words set chosen = {str(cnt)}, recent_chosen_time = datetime('now') where word = '{word}'"
        cur.execute(sql)
        con_completion.commit()
    else:
        add_word(word, '-')

DIGIT_MARKS = {
        '1': ['①', '❶', 'Ⅰ', 'ⅰ'],
        '2': ['②', '❷', 'Ⅱ', 'ⅱ'],
        '3': ['③', 'Ⅲ', 'ⅲ'],
        '4': ['④', 'Ⅳ', 'ⅳ'],
        '5': ['⑤', 'Ⅴ', 'ⅴ'],
        '6': ['⑥', 'Ⅵ', 'ⅵ'],
        '7': ['⑦', 'Ⅶ', 'ⅶ'],
        '8': ['⑧', 'Ⅷ', 'ⅷ'],
        '9': ['⑨', 'Ⅸ', 'ⅸ'],
        '10': ['⑩', 'Ⅹ', 'ⅹ'],
        '11': ['⑪'], '12': ['⑫'], '13': ['⑬'], '14': ['⑭'], '15': ['⑮'], '16': ['⑯'], '17': ['⑰'], '18': ['⑱'], '19': ['⑲'], '20': ['⑳'],
        'shikaku': ['□', '■', '◇', '◆'],
        'sannkaku': ['△', '▲', '▽', '▼'],
        'maru': ['○', '●', '◎'],
        'hoshi': ['☆', '★', '＊', '※', '⁂'],
        'migi': ['→', '㊨'], 'hidari': ['←', '㊧'], 'ue': ['↑', '㊤'], 'shita': ['↓', '㊦'],
        'euro': ['€'],
        '()': ['（）', '「」', '〔〕', '［］', '｛｝', '〈〉', '《》', '『』', '【】'],
        '(': ['（', '「', '〔', '［', '｛', '〈', '《', '『', '【'],
        ')': ['）', '」', '〕', '］', '｝', '〉', '》', '』', '】'],
        }

def print_marks(word:str, rst:list):
    """
    print marks from DIGIT_MARKS, indicated by :param word:.
    """
    for w, mks in DIGIT_MARKS.items():
        if word == w:
            rst.extend([CompletionItem(mk, 'marks') for mk in mks])

def create_gobi(created_romaji, created_kana, romaji):
    gobi_tmp = copy.deepcopy(GOBI)
    for romaji_gobi, kana_gobi in gobi_tmp.items():
        if romaji.endswith(romaji_gobi):
            create_gobi(romaji_gobi + created_romaji, kana_gobi + created_kana, romaji[:-len(romaji_gobi)])
        elif created_romaji != '':
            GOBI[created_romaji] = created_kana


def query_jp_dict(word:str):
    """
    query candidates from Japanese dictionary complition.
    :param word: word to query
    """
    rst_list = []
    con_jp_dict = sqlite3.connect(JP_DICT_DB_PATH)
    order = ' ORDER BY CHOSEN DESC, FREQUENCY DESC, LENGTH(WORD), LENGTH(PLAIN_TEXT) ASC'
    if '.' in word:
        word = word[word.index('.')+1:]
    to_query = word.replace('nn', 'n').replace('\\', '')
    # exact match original word
    sql = 'SELECT DISTINCT WORD, FREQUENCY, CHOSEN FROM JP_DICT WHERE SRC <> "create" AND PLAIN_TEXT = "{}" {}'.format(to_query, order)
    query(sql, '󰾹 match', con_jp_dict, rst_list)
    # exact match created word
    sql = 'SELECT DISTINCT WORD, FREQUENCY, CHOSEN FROM JP_DICT WHERE SRC = "create" AND PLAIN_TEXT = "{}" {}'.format(to_query, order)
    query(sql, '󰾹 created', con_jp_dict, rst_list)
    create_gobi('', '', word)
    # with 語尾
    for romaji_gobi, kana_gobi in GOBI.items():
        if word.endswith(romaji_gobi):
            without_gobi = to_query[:-len(romaji_gobi)]
            # 登る %-_u
            sql = 'SELECT DISTINCT WORD, FREQUENCY, CHOSEN FROM JP_DICT WHERE PLAIN_TEXT = "{}" and src like "%-_u" {} limit 20'.format(without_gobi[:-1] + 'u', order)
            if without_gobi[-2:] in HIRAKANA.keys():
                query_and_inflect(sql, '󰷫 Inf(_u)+語尾', HIRAKANA[without_gobi[-2:]], kana_gobi, con_jp_dict, rst_list)
            elif without_gobi[-1:] in HIRAKANA.keys():
                query_and_inflect(sql, '󰷫 Inf(_u)+語尾', HIRAKANA[without_gobi[-1:]], kana_gobi, con_jp_dict, rst_list)
            # んで
            if romaji_gobi.startswith('nd'):
                sql = 'SELECT DISTINCT WORD, FREQUENCY, CHOSEN FROM JP_DICT WHERE PLAIN_TEXT = "{}" and src like "%-_u" {} limit 20'.format(without_gobi + 'mu', order)
                query_and_inflect(sql, '󰷫 Inf(む)+語尾', '', kana_gobi, con_jp_dict, rst_list)
                sql = 'SELECT DISTINCT WORD, FREQUENCY, CHOSEN FROM JP_DICT WHERE PLAIN_TEXT = "{}" and src like "%-_u" {} limit 20'.format(without_gobi + 'bu', order)
                query_and_inflect(sql, '󰷫 Inf(ぶ)+語尾', '', kana_gobi, con_jp_dict, rst_list)
                sql = 'SELECT DISTINCT WORD, FREQUENCY, CHOSEN FROM JP_DICT WHERE PLAIN_TEXT = "{}" and src like "%-_u" {} limit 20'.format(without_gobi + 'nu', order)
                query_and_inflect(sql, '󰷫 Inf(ぬ)+語尾', '', kana_gobi, con_jp_dict, rst_list)
            # して
            if romaji_gobi.startswith('shit'):
                sql = 'SELECT DISTINCT WORD, FREQUENCY, CHOSEN FROM JP_DICT WHERE PLAIN_TEXT = "{}" and src like "%-_u" {} limit 20'.format(without_gobi + 'su', order)
                query_and_inflect(sql, '󰷫 Inf(す)+語尾', '', kana_gobi, con_jp_dict, rst_list)
            # いて
            if romaji_gobi.startswith('it'):
                sql = 'SELECT DISTINCT WORD, FREQUENCY, CHOSEN FROM JP_DICT WHERE PLAIN_TEXT = "{}" and src like "%-_u" {} limit 20'.format(without_gobi + 'tu', order)
                query_and_inflect(sql, '󰷫 Inf(つ)+語尾', '', kana_gobi, con_jp_dict, rst_list)
                sql = 'SELECT DISTINCT WORD, FREQUENCY, CHOSEN FROM JP_DICT WHERE PLAIN_TEXT = "{}" and src like "%-_u" {} limit 20'.format(without_gobi + 'ku', order)
                query_and_inflect(sql, '󰷫 Inf(く)+語尾', '', kana_gobi, con_jp_dict, rst_list)
            # って
            if romaji_gobi.startswith('tt'):
                sql = 'SELECT DISTINCT WORD, FREQUENCY, CHOSEN FROM JP_DICT WHERE PLAIN_TEXT = "{}" and src like "%-_u" {} limit 20'.format(without_gobi + 'ru', order)
                query_and_inflect(sql, '󰷫 Inf(る)+語尾', '', kana_gobi, con_jp_dict, rst_list)
                sql = 'SELECT DISTINCT WORD, FREQUENCY, CHOSEN FROM JP_DICT WHERE PLAIN_TEXT = "{}" and src like "%-u" {} limit 20'.format(without_gobi + 'u', order)
                query_and_inflect(sql, '󰷫 Inf(う)+語尾', '', kana_gobi, con_jp_dict, rst_list)

            # 買う %-u
            sql = 'SELECT DISTINCT WORD, FREQUENCY, CHOSEN FROM JP_DICT WHERE PLAIN_TEXT = "{}" and src like "%-u" {} limit 20'.format(without_gobi[:-2] + 'u', order)
            if without_gobi[-2:] in HIRAKANA.keys():
                query_and_inflect(sql, '󰷫 Inf(u)+語尾', HIRAKANA[without_gobi[-2:]], kana_gobi, con_jp_dict, rst_list)

            sql = 'SELECT DISTINCT WORD, FREQUENCY, CHOSEN FROM JP_DICT WHERE PLAIN_TEXT = "{}" and src like "%-adj" {}'.format(without_gobi + 'i', order)
            query_and_inflect(sql, '󰷫 い形容詞 語尾', '', kana_gobi, con_jp_dict, rst_list)
            sql = 'SELECT DISTINCT WORD, FREQUENCY, CHOSEN FROM JP_DICT WHERE PLAIN_TEXT = "{}" and src = "kunnyomi" {} LIMIT 5'.format(without_gobi, order)
            query_with_decor(sql, '󰷫 訓+語尾', con_jp_dict, kana_gobi, rst_list)
            sql = 'SELECT DISTINCT WORD, FREQUENCY, CHOSEN FROM JP_DICT WHERE PLAIN_TEXT = "{}" and src <> "kunnyomi" {}'.format(without_gobi, order)
            query_with_decor(sql, '󰷫 語尾', con_jp_dict, kana_gobi, rst_list)

    order = ' ORDER BY CHOSEN DESC, LENGTH(WORD), LENGTH(PLAIN_TEXT) ASC, FREQUENCY DESC'
    # chosen words
    sql = 'SELECT DISTINCT WORD, FREQUENCY, CHOSEN FROM JP_DICT WHERE PLAIN_TEXT LIKE "{}%" AND CHOSEN > 0 {}'.format(to_query, order)
    query(sql, '󰂺 chosen', con_jp_dict, rst_list)
    # special marks
    print_marks(word, rst_list)

    cur = con_jp_dict.cursor()
    # if '/' given then use it as delimiter
    # reverse query (for create word)
    for i in reversed(range(1, len(to_query))):
        if to_query[i-1] not in VOWELS: continue
        if re.compile(r'.*' + DELIMITATOR + '.*').match(to_query):
            l, r = to_query.split(DELIMITATOR, maxsplit=1)
        else:
            l, r = to_query[:i], to_query[i:]
        sql = 'SELECT DISTINCT WORD FROM JP_DICT WHERE PLAIN_TEXT = "{}" {} LIMIT 20'.format(l, order)
        rst = cur.execute(sql).fetchall()
        if rst:
            for item in rst:
                rst_list.append(CompletionItem(item[0] + r, '󰎔'))
            break
    # digits (currency)
    if re.compile(r'^\d*$').match(word):
        rst_list.append(CompletionItem(word, 'digit'))
        rst_list.append(CompletionItem("{:,}".format(int(word)), 'digit'))
        rst_list.append(CompletionItem(''.join(DIGITS[d] for d in [*word]), 'digit'))
        rst_list.append(CompletionItem(''.join(DIGITS[d] for d in [*"{:,}".format(int(word))]), 'digit'))

    # katakana
    result = subprocess.run(['/root/.config/nvim/romaji_hirakana', word], stdout=subprocess.PIPE)
    hirakana = result.stdout.decode('utf8').rstrip()
    result = subprocess.run(['/root/.config/nvim/hirakana_to_katakana', hirakana], stdout=subprocess.PIPE)
    rst_list.append(CompletionItem(result.stdout.decode('utf8').rstrip(), 'カタカナ'))
    # かな
    rst_list.insert(1, CompletionItem(hirakana, '平仮名')) # one candidate for quick select kana
    return rst_list

def choose_jp_dict(word:str, inserting:str):
    con_jp_dict = sqlite3.connect(JP_DICT_DB_PATH)
    cur = con_jp_dict.cursor()
    cur.execute('insert into jp_create_tmp(word, plain) values ("{}", "{}")'.format(word, inserting))
    con_jp_dict.commit()
    # logging.debug([word, inserting])
    if re.compile(r'^[\u0080-\uFFFF]*$').match(word):
        create_jp()

def add_jp_chosen_cnt(word:str, plain:str):
    # add all words that match
    con_jp_dict = sqlite3.connect(JP_DICT_DB_PATH)
    cur = con_jp_dict.cursor()
    cur.execute('select chosen from JP_DICT where word = "{}" and plain_text = "{}" limit 1'.format(word, plain))
    chosen_cnt = cur.fetchall()
    if len(chosen_cnt) == 1:
        cnt = chosen_cnt[0][0] + 1
        sql = 'update jp_dict set chosen = {} where word = "{}" and plain_text = "{}"'.format(cnt, word, plain)
        cur.execute(sql)
        con_jp_dict.commit()
    elif len(chosen_cnt) == 0: # create new one
        cur.execute('insert into jp_dict values("{}", "{}", 1, "create", 0)'.format(plain, word))
        con_jp_dict.commit()

def get_romaji_from_inserting(word:str, inserting:str) -> list:
    tail = re.compile(r'[-a-z]*$').findall(word)[0]
    if tail:
        return [word[:-len(tail)], inserting[:-len(tail)]]
    return [word, inserting]

def get_romaji_from_word(word:str) -> str:
    con_jp_dict = sqlite3.connect(JP_DICT_DB_PATH)
    cur = con_jp_dict.cursor()
    cur.execute(f'select plain_text from jp_dict where word = "{word}" limit 1')
    rst = cur.fetchall()
    return rst[0][0] if len(rst) != 0 else ''


def create_jp():
    con_jp_dict = sqlite3.connect(JP_DICT_DB_PATH)
    cur = con_jp_dict.cursor()
    cur.execute('select word from jp_create_tmp order by id asc')
    history = [item[0] for item in cur.fetchall()]
    # import all sublist of history
    n = len(history)
    sublists = []
    for start in range(n):
        for end in range(start + 1, n + 1):
            sublists.append(history[start:end])
    for sub in sublists:
        word, plain = '', ''
        for it in sub:
            _word = ''.join([c for c in it if not c.isascii()]) 
            word += _word
            plain += get_romaji_from_word(_word)
            add_jp_chosen_cnt(word, plain)

    # clear history
    cur.execute('delete from jp_create_tmp')
    con_jp_dict.commit()

def query_cn_wrap(sql_pinyin, sql_init, word):
    """
    :param sql_pinyin: query word by pinyin
    :param sql_init: query word by 声母
    """
    initials_pat = re.compile('^[qwrtypsdfghjklzxcvbnm]*$')
    if initials_pat.match(word):
        return sql_init.format(word)
    else:
        return sql_pinyin.format(word)

def query_cn_dict(word):
    rst_list = []
    con_cn_dict = sqlite3.connect(CN_DICT_DB_PATH)
    if '.' in word:
        word = word[word.index('.')+1:]
    to_query = word.replace('nn', 'n').replace('\\', '')
    # exact match created word
    sql_pinyin = '''
    SELECT DISTINCT D.WORD, D.FREQUENCY, D.CHOSEN FROM CN_DICT D JOIN PINYIN_PLAIN P ON D.WORD = P.WORD
    WHERE D.SRC = "create" AND P.PINYIN = "{}" ORDER BY D.CHOSEN DESC, D.FREQUENCY DESC, LENGTH(D.WORD) ASC
    '''
    sql_init = '''
    SELECT DISTINCT D.WORD, D.FREQUENCY, D.CHOSEN FROM CN_DICT D JOIN INITIALS I ON D.WORD = I.WORD
    WHERE D.SRC = "create" AND I.INITIAL = "{}" ORDER BY D.CHOSEN DESC, D.FREQUENCY DESC, LENGTH(D.WORD) ASC
    '''
    query(query_cn_wrap(sql_pinyin, sql_init, to_query), '󰾹 created', con_cn_dict, rst_list)
    # exact match original word
    sql_pinyin = '''
    SELECT DISTINCT D.WORD, D.FREQUENCY, D.CHOSEN FROM CN_DICT D JOIN PINYIN_PLAIN P ON D.WORD = P.WORD
    WHERE D.SRC <> "create" AND P.PINYIN = "{}" ORDER BY D.CHOSEN DESC, D.FREQUENCY DESC, LENGTH(D.WORD) ASC
    '''
    sql_init = '''
    SELECT DISTINCT D.WORD, D.FREQUENCY, D.CHOSEN FROM CN_DICT D JOIN INITIALS I ON D.WORD = I.WORD
    WHERE D.SRC <> "create" AND I.INITIAL = "{}" ORDER BY D.CHOSEN DESC, D.FREQUENCY DESC, LENGTH(D.WORD) ASC
    '''
    query(query_cn_wrap(sql_pinyin, sql_init, to_query), '󰾹 match', con_cn_dict, rst_list)

    cur = con_cn_dict.cursor()
    # if '/' given then use it as delimiter
    candidiates = []
    sql_pinyin_create = '''
    SELECT DISTINCT D.WORD, P.PINYIN FROM CN_DICT D JOIN PINYIN_PLAIN P ON D.WORD = P.WORD
    WHERE P.PINYIN IN ({}) ORDER BY D.CHOSEN DESC, D.FREQUENCY DESC, LENGTH(D.WORD) ASC
    '''
    for i in reversed(range(1, len(to_query))):
        if to_query[i] not in 'qwrtypsdfghjklzxcvbnm': continue
        if re.compile(r'.*' + DELIMITATOR + '.*').match(to_query):
            l, _ = to_query.split(DELIMITATOR, maxsplit=1)
        else:
            l, _ = to_query[:i], to_query[i:]
        candidiates.append(l)
    rst = cur.execute(sql_pinyin_create.format(','.join([f'"{c}"' for c in candidiates]))).fetchall()
    for item in rst:
        word, pin = (item[0], item[1])
        r = to_query[len(pin):]
        if r.startswith(DELIMITATOR): # remove start delimitator
            r = r[1:]
        rst_list.append(CompletionItem(item[0] + r, '󰎔'))
    return rst_list

def insert_new_cn_word(word, cursor):
    cnt = cursor.execute('select count(1) from cn_dict where word = "{}"'.format(word)).fetchall()
    if cnt[0][0] != 0:
        add_cn_chosen_cnt(word, cursor)
        return
    from xpinyin import Pinyin
    p = Pinyin()
    cursor.execute(f'insert into cn_dict values("{word}", 1, "create", 0)')
    for pin in p.get_pinyins(word):
        pin_without_half = pin.replace('-', '')
        cursor.execute(f'insert into pinyin_plain values("{word}", "{pin_without_half}")')
    for pin in p.get_pinyins(word, tone_marks='numbers'):
        pin_without_half = pin.replace('-', '')
        cursor.execute(f'insert into pinyin_plain values("{word}", "{pin_without_half}")')
    init = p.get_initials(word)
    init_without_half = init.replace('-', '').lower()
    cursor.execute(f'insert into initials values ("{word}", "{init_without_half}");')

def choose_cn_dict(word:str, inserting:str):
    con_cn_dict = sqlite3.connect(CN_DICT_DB_PATH)
    cur = con_cn_dict.cursor()
    cur.execute('insert into cn_create_tmp(word, plain) values ("{}", "{}")'.format(word, inserting))
    con_cn_dict.commit()
    if re.compile(r'^[\u0080-\uFFFF]*$').match(word):
        create_cn()

def create_cn():
    con_cn_dict = sqlite3.connect(CN_DICT_DB_PATH)
    cur = con_cn_dict.cursor()
    cur.execute('select word from cn_create_tmp order by id asc')
    history = [item[0] for item in cur.fetchall()]
    # import all sublist of history
    n = len(history)
    sublists = []
    for start in range(n):
        for end in range(start + 1, n + 1):
            sublists.append(history[start:end])
    for sub in sublists:
        word = ''
        for it in sub:
            word += ''.join([c for c in it if not c.isascii()])
            insert_new_cn_word(word, cur)
    
    # clear history
    cur.execute('delete from cn_create_tmp')
    con_cn_dict.commit()

def add_cn_chosen_cnt(word:str, cursor):
    # add all words that match
    cursor.execute('select chosen from CN_DICT where word = "{}" limit 1'.format(word))
    chosen_cnt = cursor.fetchall()
    if len(chosen_cnt) == 1:
        cnt = chosen_cnt[0][0] + 1
        sql = 'update cn_dict set chosen = {} where word = "{}"'.format(cnt, word)
        cursor.execute(sql)
    elif len(chosen_cnt) == 0: # create new one
        insert_new_cn_word(word, cursor)

def query_all_dict(word:str, use_en:bool, use_de:bool):
    rst_list = []
    exp = '^' + '.*'.join([ESCAPE[ch] if ch in ESCAPE else '['+ch+ch.upper()+']' for ch in word])
    if use_en:
        result = subprocess.run(['rg', exp, '-I', '/usr/share/dict/en'], stdout=subprocess.PIPE)
        rst = result.stdout.decode('utf8').split('\n')
        for dict_word in filter(lambda x : x != '', rst):
            rst_list.append(CompletionItem(dict_word, '󰺄 dict[Eng]', len(dict_word)))
        return sorted(rst_list, key=lambda i : i.freq)
    if use_de:
        DE_ESCAPE = {
                'a' : '[aäAÄ]',
                'i' : '[iïIÏ]',
                'u' : '[uüUÜ]',
                'e' : '[eéëEË]',
                'o' : '[oöOÖ]',
                's' : '[sSß]',
                }
        exp = '^' + '.*'.join([DE_ESCAPE[ch] if ch in DE_ESCAPE else '['+ch+ch.upper()+']' for ch in word])
        cmd = f'rg {exp} -I /usr/share/dict/ngerman' + " | awk '{ print length($0), $0; }' | sort -n | cut -d' ' -f2-"
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
        rst = result.stdout.decode('utf8').split('\n')
        for dict_word in filter(lambda x : x != '', rst):
            print(dict_word + ' 󰺄 dict[Deu]')
        exit(0)

if __name__ == '__main__':
    rst_list = []
    if sys.argv[1] == '-h':
        print('hello')
    if sys.argv[1] == '-add_path':
        paths = sys.argv[2:]
        for path_enc in set(dict.fromkeys(paths)):
            # print('adding path:', path_enc)
            path, enc = path_enc.split(':')
            if path.endswith('.log'):
                continue
            add_words(path, enc)
    if sys.argv[1] == '-add_word':
        word = sys.argv[2]
        path = sys.argv[3]
        if word.isascii():
            add_word(word, path)

    if sys.argv[1] == '-query':
        word = sys.argv[2]
        src = sys.argv[3]
        mode = int(sys.argv[4]) % TOTAL_CANDIDATES_ORDER_MODE
        rst_list = query_word(word, src, mode)
    if sys.argv[1] == '-chosen':
        chosen_word = sys.argv[2]
        if chosen_word.isascii():
            choose(chosen_word)

    if sys.argv[1] == '-query_jp':
        word = sys.argv[2]
        rst_list = query_jp_dict(word)
    if sys.argv[1] == '-chosen_jp':
        chosen_word, inserting = sys.argv[2:4]
        choose_jp_dict(chosen_word, inserting.replace(DELIMITATOR, ''))
    if sys.argv[1] == '-create':
        create_cn()
    # if sys.argv[1] == '-test':
    #     create_gobi('', '', 'atukunakunarimashita')
    #     print(GOBI)

    if sys.argv[1] == '-query_cn':
        word = sys.argv[2]
        rst_list = query_cn_dict(word)
    if sys.argv[1] == '-chosen_cn':
        chosen_word, inserting = sys.argv[2:4]
        choose_cn_dict(chosen_word, inserting.replace(DELIMITATOR, ''))

    if sys.argv[1] == '-query_en':
        word = sys.argv[2]
        rst_list = query_all_dict(word, use_en=True, use_de=False)
    if sys.argv[1] == '-query_de':
        word = sys.argv[2]
        rst_list = query_all_dict(word, use_en=False, use_de=True)
    if sys.argv[1] == '-query_all':
        word = sys.argv[2]
        rst_list = query_all_dict(word, use_en=True, use_de=True)

    for it in rst_list:
        print(it)

