#!/usr/bin/python3

import sqlite3
from xpinyin import Pinyin
from rich.progress import track

p = Pinyin()

con = sqlite3.connect('./completion.db')
cur = con.cursor()

sql = "select d.* from cn_dict d left join initials i on d.word = i.word where i.initial like '%j';"

cur.execute(sql)
for item in track(cur.fetchall()):
    word = item[0]
    for py in p.get_pinyins(word):
        inits = p.get_initials(word).split('-')[:-1]
        new_initials = ''.join(inits + py.split('-')[-1:]).lower()
        # print(word)
        # print(new_initials)
        cur2 = con.cursor()
        cur2.execute(f"select count(1) from initials where word = '{word}' and initial = '{new_initials}'")
        cnt = cur2.fetchall()[0][0]
        # print(cnt)
        if cnt == 0:
            cur3 = con.cursor()
            cur3.execute(f'insert into initials values ("{word}", "{new_initials}");')
con.commit()


