#!/usr/bin/python3

# completion_buf.db schema:
# create table words (word text, chosen int, src, recent_chosen_time datetime);
# create index idx_words on words(word, chosen);
# create table path_history (path text, hash text);
# create index idx_path_history on path_history(path, hash);

import sys
import re
import sqlite3
import logging
import subprocess
from os import access, R_OK
from os.path import isfile
from thefuzz import process
from thefuzz import fuzz
from jpn_ime_service import romaji_to_hirakana

COMPLETE_BUF_DB_PATH = '/root/.config/nvim/completion_buf.db'
DICT_DB_PATH = '/root/.config/nvim/jp/completion.db'
WORD_PAT = re.compile('(?u)([\w]{3,})')
VOWELS = 'aeiou'
DELIMITATOR = '/'

DIGITS = { '0': '０', '1': '１', '2': '２', '3': '３', '4': '４', '5': '５', '6': '６', '7': '７', '8': '８', '9': '９', ',': '，', }

MARKS = {
        '~':'～',
        '!':'！',
        '@':'＠',
        '#':'＃',
        '$':'＄',
        '%':'％',
        '^':'＾',
        '&':'＆',
        '*':'＊',
        '-':'ー',
        '<':'＜',
        '>':'＞',
        '?':'？',
        '/':'・',
        ',':'、',
        '.':'。',
        '|':'｜',
        }

GOBI = {
        'suru':'する',
        'shite':'して',
        'shimasu':'します',
        'shitemasu':'してます',
        'shiteimasu':'しています',
        'naru':'なる',
        'narimasu':'なります',
        'natte':'なって',
        'natta':'なった',
        'wo':'を',
        'ku':'く',
        'te':'て',
        'ha':'は',
        'ga':'が',
        'ni':'に',
        }

# logging.basicConfig(filename='./example.log', level=logging.DEBUG)

con = sqlite3.connect(COMPLETE_BUF_DB_PATH)
con_dict = sqlite3.connect(DICT_DB_PATH)

def query(sql, indicate, use_dict:bool):
    cur = con.cursor() if not use_dict else con_dict.cursor()
    cur.execute(sql)
    for item in cur.fetchall():
        print(item[0], indicate)

def query_with_decor(sql, indicate, use_dict:bool, tail_decor):
    cur = con.cursor() if not use_dict else con_dict.cursor()
    cur.execute(sql)
    for item in cur.fetchall():
        print(item[0] + tail_decor, indicate)

def add_word(word:str, path:str):
    cur = con.cursor()
    cur.execute('select count(1) from words where word = "' + word + '"')
    cnt = cur.fetchall()[0][0]
    if cnt == 0:
        cur.execute('insert into words values ("' + word + '", 0, "' + path + '", datetime("now"))')
    con.commit()

# return True if has history, False if no history
def has_path_history(path, hashcode):
    cur = con.cursor()
    cur.execute('select count(1) from path_history where path = "' + path + '" and hash = "' + hashcode + '"')
    cnt = cur.fetchall()[0][0]
    return cnt != 0

def add_words(path:str, enc:str):
    global words
    if not isfile(path) or not access(path, R_OK):
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
        cur = con.cursor()
        for w in tmp:
            cur.execute('select count(1) from words where word = "' + w + '"')
            cnt = cur.fetchall()[0][0]
            if cnt == 0:
                cur.execute('insert into words values ("' + w + '", 0, "' + path + '", null)')
        cur.execute('insert into path_history values ("' + path + '", "' + hashcode + '")') # add path to history
        con.commit()

def query_word(word:str):
    like_pat = '%' + '%'.join((ch for ch in word)) + '%'
    # recent hot words
    sql = '''SELECT DISTINCT WORD FROM WORDS WHERE
            LENGTH(WORD) < 100 AND WORD LIKE "''' + like_pat + '''" COLLATE NOCASE 
            AND RECENT_CHOSEN_TIME IS NOT NULL
            AND RECENT_CHOSEN_TIME >= DATETIME("NOW", "-2 HOUR")
            ORDER BY RECENT_CHOSEN_TIME DESC, CHOSEN DESC LIMIT 15'''
    query(sql, '󰈸 hot data', False)

    # chosen history
    sql = 'SELECT DISTINCT WORD FROM WORDS WHERE CHOSEN > 0 AND LENGTH(WORD) < 100 AND WORD LIKE "' + like_pat + '" COLLATE NOCASE ORDER BY CHOSEN DESC LIMIT 15'
    query(sql, '󱈅 chosen history', False)
    # unchosen words
    sql = 'SELECT DISTINCT WORD FROM WORDS WHERE LENGTH(WORD) < 100 AND WORD LIKE "' + like_pat + '" COLLATE NOCASE LIMIT 20'
    query(sql, '󰄮 unchosen', False)

def choose(word:str):
    cur = con.cursor()
    cur.execute('select chosen from words where word = "' + word + '" limit 1')
    chosen_cnt = cur.fetchall()
    if len(chosen_cnt) == 1:
        cnt = chosen_cnt[0][0] + 1
        sql = 'update words set chosen = ' + str(cnt) + ', recent_chosen_time = datetime("now") where word = "' + word + '"'
        cur.execute(sql)
        con.commit()
    else:
        add_word(word, '-')

def prints(marks):
    for mk in marks:
        print(mk)

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

def print_marks(word:str):
    for w, mks in DIGIT_MARKS.items():
        if word == w:
            prints(mks)

def query_dict(word:str):
    order = ' ORDER BY CHOSEN DESC, LENGTH(WORD), LENGTH(PLAIN_TEXT) ASC, FREQUENCY DESC'
    to_query = word.replace('nn', 'n').replace('\\', '')
    # with 語尾
    for romaji_gobi, kana_gobi in GOBI.items():
        if word.endswith(romaji_gobi):
            sql = 'SELECT DISTINCT WORD FROM JP_DICT WHERE PLAIN_TEXT LIKE "{}" {}'.format(to_query[:-len(romaji_gobi)], order)
            query_with_decor(sql, '󰷫 語尾', True, kana_gobi)
    # chosen words
    sql = 'SELECT DISTINCT WORD FROM JP_DICT WHERE PLAIN_TEXT LIKE "{}%" AND CHOSEN > 0 {}'.format(to_query, order)
    query(sql, '󰂺 chosen', True)
    # non-chosen words
    sql = 'SELECT DISTINCT WORD FROM JP_DICT WHERE PLAIN_TEXT = "{}" {}'.format(to_query, order)
    query(sql, ' non-chosen', True)
    # special marks
    print_marks(word)

    cur = con_dict.cursor()
    # if '/' given then use it as delimiter
    # reverse query (for create word)
    for i in reversed(range(1, len(to_query))):
        if to_query[i-1] not in VOWELS: continue
        if re.compile(r'.*' + DELIMITATOR + '.*').match(to_query):
            l, r = to_query.split(DELIMITATOR)
        else:
            l, r = to_query[:i], to_query[i:]
        sql = 'SELECT DISTINCT WORD FROM JP_DICT WHERE PLAIN_TEXT = "{}" {} LIMIT 20'.format(l, order)
        rst = cur.execute(sql).fetchall()
        if rst:
            for item in rst:
                print(item[0] + r, '󰎔')
            break
    # digits (currency)
    if re.compile(r'^\d*$').match(word):
        print(word)
        print("{:,}".format(int(word)))
        print(''.join(DIGITS[d] for d in [*word]))
        print(''.join(DIGITS[d] for d in [*"{:,}".format(int(word))]))

    # katakana
    result = subprocess.run(['/root/.config/nvim/romaji_hirakana', word], stdout=subprocess.PIPE)
    katakana = result.stdout.decode('utf8')
    result = subprocess.run(['/root/.config/nvim/hirakana_to_katakana', katakana], stdout=subprocess.PIPE)
    print(result.stdout.decode('utf8'))

def choose_dict(word:str, inserting:str):
    cur = con_dict.cursor()
    cur.execute('insert into jp_create_tmp(word, plain) values ("{}", "{}")'.format(word, inserting))
    con_dict.commit()
    # logging.debug([word, inserting])
    if re.compile(r'^[\u0080-\uFFFF]*$').match(word):
        create()

def add_chosen_cnt(word:str, plain:str):
    # add all words that match
    cur = con_dict.cursor()
    cur.execute('select chosen from JP_DICT where word = "{}" and plain_text = "{}" limit 1'.format(word, plain))
    chosen_cnt = cur.fetchall()
    if len(chosen_cnt) == 1:
        cnt = chosen_cnt[0][0] + 1
        sql = 'update jp_dict set chosen = {} where word = "{}" and plain_text = "{}"'.format(cnt, word, plain)
        cur.execute(sql)
        con_dict.commit()
    elif len(chosen_cnt) == 0: # create new one
        cur.execute('insert into jp_dict values("{}", "{}", 1, "create", 0)'.format(plain, word))
        con_dict.commit()

def get_romaji_from_inserting(word, inserting):
    tail = re.compile(r'[-a-z]*$').findall(word)[0]
    if tail:
        return [word[:-len(tail)], inserting[:-len(tail)]]
    return [word, inserting]


def create():
    cur = con_dict.cursor()
    cur.execute('select word, plain from jp_create_tmp order by id asc')
    history = [(item[0], item[1]) for item in cur.fetchall()]
    last_item_word, last_item_plain = history[-1]
    if re.compile(r'^[\u0080-\uFFFF]*$').match(last_item_word) and len(history) == 1: # just increase chosen cnt
        add_chosen_cnt(last_item_word, last_item_plain)
    elif re.compile(r'^[\u0080-\uFFFF]*$').match(last_item_word) and len(history) > 1: # create new expression
        word = ''
        _, first_word_romaji = history[0]
        for it in history:
            _word, _plain = it
            _wodr_to_add, _plain_to_add = get_romaji_from_inserting(_word, _plain)
            add_chosen_cnt(_wodr_to_add, _plain_to_add) # add cnt for every chosen word in history
            word += re.compile(r'^[\u0080-\uFFFF]*').findall(_word)[0]
        cnt = cur.execute('select count(1) from jp_dict where plain_text = "{}" and word = "{}"'.format(first_word_romaji, word)).fetchall()
        if cnt[0][0] == 0:
            cur.execute('insert into jp_dict values("{}", "{}", 1, "create", 0)'.format(first_word_romaji, word))
            con_dict.commit()
    # clear history
    cur.execute('delete from jp_create_tmp')
    con_dict.commit()


if __name__ == '__main__':
    if sys.argv[1] == '-h':
        print('hello')
    if sys.argv[1] == '-add_path':
        paths = sys.argv[2:]
        for path_enc in set(dict.fromkeys(paths)):
            print('adding path:', path_enc)
            path, enc = path_enc.split(':')
            add_words(path, enc)
    if sys.argv[1] == '-add_word':
        word = sys.argv[2]
        path = sys.argv[3]
        add_word(word, path)

    if sys.argv[1] == '-query':
        word = sys.argv[2]
        query_word(word)
    if sys.argv[1] == '-chosen':
        chosen_word = sys.argv[2]
        choose(chosen_word)

    if sys.argv[1] == '-query_d':
        word = sys.argv[2]
        query_dict(word)
    if sys.argv[1] == '-chosen_d':
        # logging.debug(sys.argv)
        chosen_word, inserting = sys.argv[2:4]
        choose_dict(chosen_word, inserting.replace(DELIMITATOR, ''))
    if sys.argv[1] == '-create':
        create()
    if sys.argv[1] == '-test':
        chosen_word, inserting = sys.argv[2:4]
        print(get_romaji_from_inserting(chosen_word, inserting))

