#!/usr/bin/python3

import sqlite3
import xpinyin
import pandas as pd
from rich.progress import track
from datetime import datetime

def insert_character_sql(word, freq, pinyin):
    if isinstance(pinyin, datetime):
        pinyin_list = ['jun' + pinyin.strftime('%d')]
    elif isinstance(pinyin, float):
        # print(pinyin)
        return ''
    else:
        # pinyin should be separated by '/'
        pinyin_list = pinyin.split('/')

    sql = 'insert into cn_dict (word'
    for i, _ in enumerate(pinyin_list, start=1):
        sql += f',pinyin_plain{i},pinyin_mark{i}'
    sql += ',chosen, frequency) values ("'
    sql += word
    sql += '"'
    for pin in pinyin_list:
        sql += (',"' + ''.join([c for c in pin if not c.isdigit()]) + '","' + pin + '"')
    sql += (',0,' + str(freq) + ');')
    return sql

con = sqlite3.connect('./completion.db')
cur = con.cursor()

cur.execute('drop table if exists cn_dict;')
# cur.execute('drop table if exists jp_create_tmp;')
# cur.execute('drop table if exists jp_gobi;')

cur.execute('''
create table cn_dict (word text,
pinyin_plain1 text,
pinyin_plain2 text,
pinyin_plain3 text,
pinyin_plain4 text,
pinyin_plain5 text,
pinyin_plain6 text,
pinyin_plain7 text,
pinyin_mark1 text,
pinyin_mark2 text,
pinyin_mark3 text,
pinyin_mark4 text,
pinyin_mark5 text,
pinyin_mark6 text,
pinyin_mark7 text,
chosen int,
src text,
frequency numeric);
            ''')

# reading characters
ch_df = pd.read_excel('./CharFreq-Combined.xls')
# print(ch_df[ch_df['character'] == '的'])

for i, row in track(ch_df.iterrows(), description='import 漢字'):
    word, freq, pinyin = row
    cur.execute(insert_character_sql(word, freq, pinyin))

con.commit()
