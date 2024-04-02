#!/usr/bin/python3

import sqlite3
from xpinyin import Pinyin
import pandas as pd
import re
from rich.progress import track
from datetime import datetime

p = Pinyin()

con = sqlite3.connect('./completion.db')
cur = con.cursor()

words_to_import = {}
words_src = {}

def insert_character_sql(word, freq, pinyin):
    if isinstance(pinyin, datetime):
        pinyin_list = ['jun' + pinyin.strftime('%d')]
    elif isinstance(pinyin, float):
        # print(pinyin)
        return ''
    else:
        # pinyin should be separated by '/'
        pinyin_list = pinyin.split('/')

    sqls = [f'insert into cn_dict values ("{word}", 0, "CharFreq-Combined.xls", {freq});']
    for pin in pinyin_list:
        pin_plain = ''.join([c for c in pin if not c.isdigit()])
        sqls.append(f'insert into pinyin_plain values ("{word}", "{pin_plain}");')
        if 'ng' in pin_plain:
            pin_without_hby = pin_plain.replace('ng', 'n') # 去掉后鼻音
            sqls.append(f'insert into pinyin_plain values ("{word}", "{pin_without_hby}");')
        if 'u' in pin_plain:
            pin_replace_v = pin_plain.replace('u', 'v')
            sqls.append(f'insert into pinyin_plain values ("{word}", "{pin_replace_v}");')
        sqls.append(f'insert into pinyin_mark values ("{word}", "{pin}");')
    return sqls

def insert_word_sql(word, freq, src):
    pin_plains = p.get_pinyins(word)
    pin_marks = p.get_pinyins(word, tone_marks='numbers')
    if len(pin_plains) == 0:
        print(f'lack of pinyin plain: {word}')
    if len(pin_marks) == 0:
        print(f'lack of pinyin mark: {word}')
    sqls = []
    sqls.append(f'insert into cn_dict values("{word}", 0, "{src}", {freq});')
    for pin in pin_plains:
        pin_without_half = pin.replace('-', '')
        sqls.append(f'insert into pinyin_plain values ("{word}", "{pin_without_half}");')
        if 'ng' in pin_without_half:
            pin_without_hby = pin_without_half.replace('ng', 'n') # 去掉后鼻音
            sqls.append(f'insert into pinyin_plain values ("{word}", "{pin_without_hby}");')
        if 'u' in pin_without_half:
            pin_replace_v = pin_without_half.replace('u', 'v')
            sqls.append(f'insert into pinyin_plain values ("{word}", "{pin_replace_v}");')
    for pin in pin_marks:
        pin_without_half = pin.replace('-', '')
        sqls.append(f'insert into pinyin_mark values ("{word}", "{pin_without_half}");')
    init = p.get_initials(word)
    init_without_half = init.replace('-', '').lower()
    sqls.append(f'insert into initials values ("{word}", "{init_without_half}");')
    return sqls


cur.execute('drop table if exists cn_dict;')
cur.execute('drop table if exists pinyin_plain;')
cur.execute('drop table if exists pinyin_mark;')
cur.execute('drop table if exists initials;')
cur.execute('drop table if exists cn_create_tmp;')
# word table
cur.execute('create table cn_dict (word text, chosen int, src text, frequency numeric);')
# pinyin tables
cur.execute('create table pinyin_plain (word text, pinyin text);')
cur.execute('create table pinyin_mark (word text, pinyin text);')
cur.execute('create table initials (word text, initial text);')
# create
cur.execute('create table cn_create_tmp (id integer primary key autoincrement, plain text, word text);')

# reading characters
ch_df = pd.read_excel('./CharFreq-Combined.xls')
# print(ch_df[ch_df['character'] == '的'])

for i, row in track(ch_df.iterrows(), description='import 漢字'):
    word, freq, pinyin = row
    sqls = insert_character_sql(word, freq, pinyin)
    for sql in sqls:
        cur.execute(sql)

con.commit()

def not_need_word(word:str) -> bool:
    if len(word) < 2:
        return True
    if re.match(r'[0-9a-zA-Z-]+', word):
        return True
    return False

def import_file(fname):
    with open(fname) as f:
        for line in track(f, description=f'reading {fname:45}'):
            if len(line.rstrip().split('	')) != 2:
                print(line)
            [word, freq] = line.rstrip().split('	')
            if not not_need_word(word) and word not in words_to_import:
                words_to_import[word] = int(freq)
                words_src[word] = fname

import_file('./blogs_wordfreq.release_UTF-8.txt')
import_file('./global_wordfreq.release_UTF-8.txt')
import_file('./literature_wordfreq.release_UTF-8.txt')
import_file('./news_wordfreq.release_UTF-8.txt')
import_file('./technology_wordfreq.release_UTF-8.txt')
import_file('./weibo_wordfreq.release_UTF-8.txt')

print(f'{len(words_to_import)} to import ...')
for word, freq in track(words_to_import.items(), description='import words'):
    src = words_src[word] if word in words_to_import else ''
    sqls = insert_word_sql(word, freq, src)
    for sql in sqls:
        cur.execute(sql)

# indices
index_sqls = [
        'create index cn_idx on cn_dict (word);',
        'create index pyp_idx on pinyin_plain (word);',
        'create index pym_idx on pinyin_mark (word);',
        'create index init_idx on initials (word);',
        'create index pyp_search_idx on pinyin_plain (word, pinyin);',
        'create index pym_search_idx on pinyin_mark (word, pinyin);',
        'create index init_search_idx on initials (word, initial);',
        'create index pyp_search_idx2 on pinyin_plain (pinyin);',
        'create index pym_search_idx2 on pinyin_mark (pinyin);',
        'create index init_search_idx2 on initials (initial);',
        ]
for idx_sql in track(index_sqls, description='creating indices...'):
    cur.execute(idx_sql)

con.commit()
