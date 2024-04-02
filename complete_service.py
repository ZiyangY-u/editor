#!/usr/bin/python3

# completion_buf.db schema:
# create table words (word text, chosen int, src, recent_chosen_time datetime, import_date datetime);
# create index idx_words on words(word, chosen);
# create index idx_words_src on words(src);
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
from jpn_ime_service import romaji_to_hirakana, HIRAKANA

COMPLETE_BUF_DB_PATH = '/root/.config/nvim/completion_buf.db'
JP_DICT_DB_PATH = '/root/.config/nvim/jp/completion.db'
CN_DICT_DB_PATH = '/root/.config/nvim/cn/completion.db'
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

def query(sql:str, indicate:str, connection:sqlite3.Connection) -> None:
    """
    query from completion db and print result
    :param sql: sql for query
    :param indicate: indicator print after every result
    :param use_dict: use Japanese dictionary if True
    """
    cur = connection.cursor()
    cur.execute(sql)
    for item in cur.fetchall():
        print(item[0], indicate)

def query_with_decor(sql:str, indicate:str, connection:sqlite3.Connection, tail_decor:str) -> None:
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
        print(item[0] + tail_decor, indicate)

def query_and_inflect(sql:str, indicate:str, patch:str, tail_decor:str, connection:sqlite3.Connection):
    cur = connection.cursor()
    cur.execute(sql)
    # logging.debug(sql)
    for item in cur.fetchall():
        print(item[0][:-1] + patch + tail_decor, indicate)

def add_word(word:str, path:str) -> None:
    """
    add word to words table.
    :param word: word to add
    :param path: word source path
    """
    con_completion = sqlite3.connect(COMPLETE_BUF_DB_PATH)
    cur = con_completion.cursor()
    cur.execute('select count(1) from words where word = "' + word + '"')
    cnt = cur.fetchall()[0][0]
    if cnt == 0:
        cur.execute('insert into words values ("' + word + '", 0, "' + path + '", datetime("now"), datetime("now"))')
    con_completion.commit()

def has_path_history(path:str, hashcode:str) -> bool:
    """
    return True if has history, False if no history.
    :param path: target file path
    :param hashcode: file's hash code
    """
    con_completion = sqlite3.connect(COMPLETE_BUF_DB_PATH)
    cur = con_completion.cursor()
    cur.execute('select count(1) from path_history where path = "' + path + '" and hash = "' + hashcode + '"')
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
            cur.execute('select count(1) from words where word = "' + w + '"')
            cnt = cur.fetchall()[0][0]
            if cnt == 0:
                cur.execute('insert into words values ("' + w + '", 0, "' + path + '", null, datetime("now"))')
        cur.execute('insert into path_history values ("' + path + '", "' + hashcode + '", datetime("now"))') # add path to history
        con_completion.commit()


def query_word(word:str, src:str) -> None:
    """
    get candidates from word complition
    :param word: word to query
    :param src: source path indication
    """
    con_completion = sqlite3.connect(COMPLETE_BUF_DB_PATH)
    # create like pattern: query -> %q%u%e%r%y%
    like_pat = '%' + '%'.join((ch for ch in word)) + '%'
    # recent hot words, recent 2 hours chosen
    sql = '''SELECT DISTINCT WORD FROM WORDS WHERE
            LENGTH(WORD) < 100 AND WORD LIKE "''' + like_pat + '''" COLLATE NOCASE
            AND RECENT_CHOSEN_TIME IS NOT NULL
            AND RECENT_CHOSEN_TIME >= DATETIME("NOW", "-2 HOUR")
            ORDER BY RECENT_CHOSEN_TIME DESC, CHOSEN DESC LIMIT 5'''
    query(sql, '󰈸 hot data', con_completion)

    # from current file
    sql = 'SELECT DISTINCT WORD FROM WORDS WHERE SRC="' + src + '" AND WORD LIKE "' + like_pat + '" COLLATE NOCASE ORDER BY CHOSEN DESC LIMIT 5'
    query(sql, '󰈝 this file', con_completion)
    # chosen history
    sql = 'SELECT DISTINCT WORD FROM WORDS WHERE CHOSEN > 0 AND LENGTH(WORD) < 100 AND WORD LIKE "' + like_pat + '" COLLATE NOCASE ORDER BY CHOSEN DESC LIMIT 15'
    query(sql, '󱈅 chosen history', con_completion)
    # unchosen words
    sql = 'SELECT DISTINCT WORD FROM WORDS WHERE LENGTH(WORD) < 100 AND WORD LIKE "' + like_pat + '" COLLATE NOCASE ORDER BY LENGTH(WORD) LIMIT 20'
    query(sql, '󰄮 unchosen', con_completion)

def choose(word:str) -> None:
    """
    add chosen :param word: count in complition db.
    if word not exists add it
    """
    con_completion = sqlite3.connect(COMPLETE_BUF_DB_PATH)
    cur = con_completion.cursor()
    cur.execute('select chosen from words where word = "' + word + '" limit 1')
    chosen_cnt = cur.fetchall()
    if len(chosen_cnt) == 1:
        cnt = chosen_cnt[0][0] + 1
        sql = 'update words set chosen = ' + str(cnt) + ', recent_chosen_time = datetime("now") where word = "' + word + '"'
        cur.execute(sql)
        con_completion.commit()
    else:
        add_word(word, '-')

def prints(marks:list) -> None:
    """
    prints marks in a list.
    """
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
    """
    print marks from DIGIT_MARKS, indicated by :param word:.
    """
    for w, mks in DIGIT_MARKS.items():
        if word == w:
            prints(mks)

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
    con_jp_dict = sqlite3.connect(JP_DICT_DB_PATH)
    order = ' ORDER BY CHOSEN DESC, FREQUENCY DESC, LENGTH(WORD), LENGTH(PLAIN_TEXT) ASC'
    if '.' in word:
        word = word[word.index('.')+1:]
    to_query = word.replace('nn', 'n').replace('\\', '')
    # exact match
    sql = 'SELECT DISTINCT WORD FROM JP_DICT WHERE PLAIN_TEXT = "{}" {}'.format(to_query, order)
    query(sql, '󰾹 match', con_jp_dict)
    create_gobi('', '', word)
    # with 語尾
    for romaji_gobi, kana_gobi in GOBI.items():
        if word.endswith(romaji_gobi):
            without_gobi = to_query[:-len(romaji_gobi)]
            # 登る %-_u
            sql = 'SELECT DISTINCT WORD FROM JP_DICT WHERE PLAIN_TEXT = "{}" and src like "%-_u" {} limit 20'.format(without_gobi[:-1] + 'u', order)
            if without_gobi[-2:] in HIRAKANA.keys():
                query_and_inflect(sql, '󰷫 Inf(_u)+語尾', HIRAKANA[without_gobi[-2:]], kana_gobi, con_jp_dict)
            elif without_gobi[-1:] in HIRAKANA.keys():
                query_and_inflect(sql, '󰷫 Inf(_u)+語尾', HIRAKANA[without_gobi[-1:]], kana_gobi, con_jp_dict)
            # んで
            if romaji_gobi.startswith('nd'):
                sql = 'SELECT DISTINCT WORD FROM JP_DICT WHERE PLAIN_TEXT = "{}" and src like "%-_u" {} limit 20'.format(without_gobi + 'mu', order)
                query_and_inflect(sql, '󰷫 Inf(む)+語尾', '', kana_gobi, con_jp_dict)
                sql = 'SELECT DISTINCT WORD FROM JP_DICT WHERE PLAIN_TEXT = "{}" and src like "%-_u" {} limit 20'.format(without_gobi + 'bu', order)
                query_and_inflect(sql, '󰷫 Inf(ぶ)+語尾', '', kana_gobi, con_jp_dict)
                sql = 'SELECT DISTINCT WORD FROM JP_DICT WHERE PLAIN_TEXT = "{}" and src like "%-_u" {} limit 20'.format(without_gobi + 'nu', order)
                query_and_inflect(sql, '󰷫 Inf(ぬ)+語尾', '', kana_gobi, con_jp_dict)
            # して
            if romaji_gobi.startswith('shit'):
                sql = 'SELECT DISTINCT WORD FROM JP_DICT WHERE PLAIN_TEXT = "{}" and src like "%-_u" {} limit 20'.format(without_gobi + 'su', order)
                query_and_inflect(sql, '󰷫 Inf(す)+語尾', '', kana_gobi, con_jp_dict)
            # いて
            if romaji_gobi.startswith('it'):
                sql = 'SELECT DISTINCT WORD FROM JP_DICT WHERE PLAIN_TEXT = "{}" and src like "%-_u" {} limit 20'.format(without_gobi + 'tu', order)
                query_and_inflect(sql, '󰷫 Inf(つ)+語尾', '', kana_gobi, con_jp_dict)
                sql = 'SELECT DISTINCT WORD FROM JP_DICT WHERE PLAIN_TEXT = "{}" and src like "%-_u" {} limit 20'.format(without_gobi + 'ku', order)
                query_and_inflect(sql, '󰷫 Inf(く)+語尾', '', kana_gobi, con_jp_dict)
            # って
            if romaji_gobi.startswith('tt'):
                sql = 'SELECT DISTINCT WORD FROM JP_DICT WHERE PLAIN_TEXT = "{}" and src like "%-_u" {} limit 20'.format(without_gobi + 'ru', order)
                query_and_inflect(sql, '󰷫 Inf(る)+語尾', '', kana_gobi, con_jp_dict)
                sql = 'SELECT DISTINCT WORD FROM JP_DICT WHERE PLAIN_TEXT = "{}" and src like "%-u" {} limit 20'.format(without_gobi + 'u', order)
                query_and_inflect(sql, '󰷫 Inf(う)+語尾', '', kana_gobi, con_jp_dict)

            # 買う %-u
            sql = 'SELECT DISTINCT WORD FROM JP_DICT WHERE PLAIN_TEXT = "{}" and src like "%-u" {} limit 20'.format(without_gobi[:-2] + 'u', order)
            if without_gobi[-2:] in HIRAKANA.keys():
                query_and_inflect(sql, '󰷫 Inf(u)+語尾', HIRAKANA[without_gobi[-2:]], kana_gobi, con_jp_dict)

            sql = 'SELECT DISTINCT WORD FROM JP_DICT WHERE PLAIN_TEXT = "{}" and src like "%-adj" {}'.format(without_gobi + 'i', order)
            query_and_inflect(sql, '󰷫 い形容詞 語尾', '', kana_gobi, con_jp_dict)
            sql = 'SELECT DISTINCT WORD FROM JP_DICT WHERE PLAIN_TEXT = "{}" and src = "kunnyomi" {} LIMIT 5'.format(without_gobi, order)
            query_with_decor(sql, '󰷫 訓+語尾', con_jp_dict, kana_gobi)
            sql = 'SELECT DISTINCT WORD FROM JP_DICT WHERE PLAIN_TEXT = "{}" and src <> "kunnyomi" {}'.format(without_gobi, order)
            query_with_decor(sql, '󰷫 語尾', con_jp_dict, kana_gobi)

    order = ' ORDER BY CHOSEN DESC, LENGTH(WORD), LENGTH(PLAIN_TEXT) ASC, FREQUENCY DESC'
    # chosen words
    sql = 'SELECT DISTINCT WORD FROM JP_DICT WHERE PLAIN_TEXT LIKE "{}%" AND CHOSEN > 0 {}'.format(to_query, order)
    query(sql, '󰂺 chosen', con_jp_dict)
    # special marks
    print_marks(word)

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


def create_jp():
    con_jp_dict = sqlite3.connect(JP_DICT_DB_PATH)
    cur = con_jp_dict.cursor()
    cur.execute('select word, plain from jp_create_tmp order by id asc')
    history = [(item[0], item[1]) for item in cur.fetchall()]
    last_item_word, last_item_plain = history[-1]
    if re.compile(r'^[\u0080-\uFFFF]*$').match(last_item_word) and len(history) == 1: # just increase chosen cnt
        add_jp_chosen_cnt(last_item_word, last_item_plain)
    elif re.compile(r'^[\u0080-\uFFFF]*$').match(last_item_word) and len(history) > 1: # create new expression
        word = ''
        _, first_word_romaji = history[0]
        for it in history:
            _word, _plain = it
            _wodr_to_add, _plain_to_add = get_romaji_from_inserting(_word, _plain)
            add_jp_chosen_cnt(_wodr_to_add, _plain_to_add) # add cnt for every chosen word in history
            word += re.compile(r'^[\u0080-\uFFFF]*').findall(_word)[0]
        cnt = cur.execute('select count(1) from jp_dict where plain_text = "{}" and word = "{}"'.format(first_word_romaji, word)).fetchall()
        if cnt[0][0] == 0:
            cur.execute('insert into jp_dict values("{}", "{}", 1, "create", 0)'.format(first_word_romaji, word))
            con_jp_dict.commit()
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
    con_cn_dict = sqlite3.connect(CN_DICT_DB_PATH)
    if '.' in word:
        word = word[word.index('.')+1:]
    to_query = word.replace('nn', 'n').replace('\\', '')
    # exact match
    sql_pinyin = '''
    SELECT DISTINCT D.WORD FROM CN_DICT D JOIN PINYIN_PLAIN P ON D.WORD = P.WORD
    WHERE P.PINYIN = "{}" ORDER BY D.CHOSEN DESC, D.FREQUENCY DESC, LENGTH(D.WORD) ASC
    '''
    sql_init = '''
    SELECT DISTINCT D.WORD FROM CN_DICT D JOIN INITIALS I ON D.WORD = I.WORD
    WHERE I.INITIAL = "{}" ORDER BY D.CHOSEN DESC, D.FREQUENCY DESC, LENGTH(D.WORD) ASC
    '''
    query(query_cn_wrap(sql_pinyin, sql_init, to_query), '󰾹 match', con_cn_dict)

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
        print(item[0] + r, '󰎔')

def insert_new_cn_word(word, cursor):
    cnt = cursor.execute('select count(1) from cn_dict where word = "{}"'.format(word)).fetchall()
    if cnt[0][0] != 0:
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

def add_cn_chosen_cnt(word:str):
    # add all words that match
    con_cn_dict = sqlite3.connect(CN_DICT_DB_PATH)
    cur = con_cn_dict.cursor()
    cur.execute('select chosen from CN_DICT where word = "{}" limit 1'.format(word))
    chosen_cnt = cur.fetchall()
    if len(chosen_cnt) == 1:
        cnt = chosen_cnt[0][0] + 1
        sql = 'update cn_dict set chosen = {} where word = "{}"'.format(cnt, word)
        cur.execute(sql)
    elif len(chosen_cnt) == 0: # create new one
        insert_new_cn_word(word, cur)
    con_cn_dict.commit()


if __name__ == '__main__':
    if sys.argv[1] == '-h':
        print('hello')
    if sys.argv[1] == '-add_path':
        paths = sys.argv[2:]
        for path_enc in set(dict.fromkeys(paths)):
            # print('adding path:', path_enc)
            path, enc = path_enc.split(':')
            add_words(path, enc)
        # clear not chosen words imported 1 days ago
        # and they will be recruited next time the file involved
        con_completion = sqlite3.connect(COMPLETE_BUF_DB_PATH)
        cur = con_completion.cursor()
        cur.execute('delete from words where chosen = 0 and import_date < datetime("now", "-1 day")')
        cur.execute('delete from path_history where import_date < datetime("now", "-1 day")')
        con_completion.commit()
    if sys.argv[1] == '-add_word':
        word = sys.argv[2]
        path = sys.argv[3]
        add_word(word, path)

    if sys.argv[1] == '-query':
        word = sys.argv[2]
        src = sys.argv[3]
        query_word(word, src)
    if sys.argv[1] == '-chosen':
        chosen_word = sys.argv[2]
        choose(chosen_word)

    if sys.argv[1] == '-query_jp':
        word = sys.argv[2]
        query_jp_dict(word)
    if sys.argv[1] == '-chosen_jp':
        chosen_word, inserting = sys.argv[2:4]
        choose_jp_dict(chosen_word, inserting.replace(DELIMITATOR, ''))
    if sys.argv[1] == '-create':
        create_cn()
    if sys.argv[1] == '-test':
        create_gobi('', '', 'atukunakunarimashita')
        print(GOBI)

    if sys.argv[1] == '-query_cn':
        word = sys.argv[2]
        query_cn_dict(word)
    if sys.argv[1] == '-chosen_cn':
        chosen_word, inserting = sys.argv[2:4]
        choose_cn_dict(chosen_word, inserting.replace(DELIMITATOR, ''))

