#!/usr/bin/python3

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

# logging.basicConfig(filename='./example.log', level=logging.DEBUG)

con = sqlite3.connect(COMPLETE_BUF_DB_PATH)
con_dict = sqlite3.connect(DICT_DB_PATH)

def query(sql, indicate, use_dict:bool):
    cur = con.cursor() if not use_dict else con_dict.cursor()
    cur.execute(sql)
    for item in cur.fetchall():
        print(item[0], indicate)

def add_word(word:str, path:str):
    cur = con.cursor()
    cur.execute('select count(1) from words where word = "' + word + '"')
    cnt = cur.fetchall()[0][0]
    if cnt == 0:
        cur.execute('insert into words values ("' + word + '", 0, "' + path + '", datetime("now"))')
    con.commit()

def add_words(path:str, enc:str):
    global words
    if not isfile(path) or not access(path, R_OK):
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
        con.commit()

def query_word(word:str):
    like_pat = '%' + '%'.join((ch for ch in word)) + '%'
    # recent hot words
    sql = '''SELECT DISTINCT WORD FROM WORDS WHERE
            LENGTH(WORD) < 100 AND WORD LIKE "''' + like_pat + '''" COLLATE NOCASE 
            AND RECENT_CHOSEN_TIME >= DATETIME("NOW", "-2 HOUR")
            AND RECENT_CHOSEN_TIME IS NOT NULL
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

def print_marks(word:str):
    if word == '1':
        prints(['①', '❶', 'Ⅰ', 'ⅰ'])
    if word == '2':
        prints(['②', '❷', 'Ⅱ', 'ⅱ'])
    if word == '3':
        prints(['③', 'Ⅲ', 'ⅲ'])
    if word == '4':
        prints(['④', 'Ⅳ', 'ⅳ'])
    if word == '5':
        prints(['⑤', 'Ⅴ', 'ⅴ'])
    if word == '6':
        prints(['⑥', 'Ⅵ', 'ⅵ'])
    if word == '7':
        prints(['⑦', 'Ⅶ', 'ⅶ'])
    if word == '8':
        prints(['⑧', 'Ⅷ', 'ⅷ'])
    if word == '9':
        prints(['⑨', 'Ⅸ', 'ⅸ'])
    if word == '10':
        prints(['⑩', 'Ⅹ', 'ⅹ'])
    if word == '11':
        prints(['⑪'])
    if word == '12':
        prints(['⑫'])
    if word == '13':
        prints(['⑬'])
    if word == '14':
        prints(['⑭'])
    if word == '15':
        prints(['⑮'])
    if word == '16':
        prints(['⑯'])
    if word == '17':
        prints(['⑰'])
    if word == '18':
        prints(['⑱'])
    if word == '19':
        prints(['⑲'])
    if word == '20':
        prints(['⑳'])
    if word == 'shikaku':
        prints(['□', '■', '◇', '◆'])
    if word == 'sannkaku':
        prints(['△', '▲', '▽', '▼'])
    if word == 'maru':
        prints(['○', '●', '◎'])
    if word == 'hoshi':
        prints(['☆', '★', '＊', '※', '⁂'])
    if word == 'migi':
        prints(['→', '㊨'])
    if word == 'hidari':
        prints(['←', '㊧'])
    if word == 'ue':
        prints(['↑', '㊤'])
    if word == 'shita':
        prints(['↓', '㊦'])
    if word == 'euro':
        prints(['€'])
        
def print_mark_seq(word:str):
    if word == '()':
        print('（）')
        print('「」')
        print('〔〕')
        print('［］')
        print('｛｝')
        print('〈〉')
        print('《》')
        print('『』')
        print('【】')
    # else:
    #     for ch in word:
    #         print(MARKS[ch] if ch in MARKS else '', end='')
                 

def query_dict(word:str):
    order = ' ORDER BY CHOSEN DESC, LENGTH(WORD), LENGTH(PLAIN_TEXT) ASC, FREQUENCY DESC'
    to_query = word.replace('nn', 'n').replace('\\', '')
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
    # kunyomi construct
    for i in reversed(range(1, len(to_query))):
        if to_query[i-1] not in VOWELS: continue
        if re.compile(r'.*' + DELIMITATOR + '.*').match(to_query):
            l, r = to_query.split(DELIMITATOR)
        else:
            l, r = to_query[:i], to_query[i:]
        # print(l, r)
        sql = 'SELECT DISTINCT WORD FROM JP_DICT WHERE PLAIN_TEXT = "{}" and src = "kunnyomi" {} LIMIT 5'.format(l, order)
        rst = cur.execute(sql).fetchall()
        if rst:
            for item in rst:
                print(item[0] + romaji_to_hirakana(r), '訓')

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

    if re.compile(r'^[ -~]*$').match(word):
        print_mark_seq(word)

    # katakana
    result = subprocess.run(['/mnt/c/Users/ziyan/OneDrive/ultisnips/romaji_hirakana', word], stdout=subprocess.PIPE)
    katakana = result.stdout.decode('utf8')
    result = subprocess.run(['/mnt/c/Users/ziyan/OneDrive/ultisnips/hirakana_to_katakana', katakana], stdout=subprocess.PIPE)
    print(result.stdout.decode('utf8'))

def choose_dict(word:str, inserting:str):
    cur = con_dict.cursor()
    cur.execute('insert into jp_create_tmp(word, plain) values ("{}", "{}")'.format(word, inserting))
    con_dict.commit()
    # logging.debug([word, inserting])
    if re.compile(r'^[\u0080-\uFFFF]*$').match(word):
        create()

def get_romaji(word:str):
    cur = con_dict.cursor()
    romaji = cur.execute('select plain_text from jp_dict where word = "{}" limit 1'.format(word)).fetchall()
    if len(romaji) == 0:
        return ''
    else:
        return romaji[0][0]

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
    lats_item_word, last_item_plain = history[-1]
    if re.compile(r'^[\u0080-\uFFFF]*$').match(lats_item_word) and len(history) == 1: # just increase chosen cnt
        add_chosen_cnt(lats_item_word, last_item_plain)
    elif re.compile(r'^[\u0080-\uFFFF]*$').match(lats_item_word) and len(history) > 1: # create new expression
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

