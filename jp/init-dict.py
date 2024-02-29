#!/usr/bin/python3

from unidecode import unidecode
from html.parser import HTMLParser
from rich.progress import track
from urllib import parse
import httpx
import sqlite3
import time
import re
import romkan

KANA_MAP = {
        'っ':'ッ',
        'ぁ':'ァ', 'あ':'ア', 'ぃ':'ィ', 'い':'イ', 'ぅ':'ゥ', 'う':'ウ', 'ぇ':'ェ', 'え':'エ', 'ぉ':'ォ', 'お':'オ',
        'か':'カ', 'が':'ガ', 'き':'キ', 'ぎ':'ギ', 'く':'ク', 'ぐ':'グ', 'け':'ケ', 'げ':'ゲ', 'こ':'コ', 'ご':'ゴ',
        'さ':'サ', 'ざ':'ザ', 'し':'シ', 'じ':'ジ', 'す':'ス', 'ず':'ズ', 'せ':'セ', 'ぜ':'ゼ', 'そ':'ソ', 'ぞ':'ゾ',
        'た':'タ', 'だ':'ダ', 'ち':'チ', 'ぢ':'ヂ', 'つ':'ツ', 'づ':'ヅ', 'て':'テ', 'で':'デ', 'と':'ト', 'ど':'ド',
        'な':'ナ', 'に':'ニ', 'ぬ':'ヌ', 'ね':'ネ', 'の':'ノ',
        'は':'ハ', 'ば':'バ', 'ぱ':'パ', 'ひ':'ヒ', 'び':'ビ', 'ぴ':'ピ', 'ふ':'フ', 'ぶ':'ブ', 'ぷ':'プ', 'へ':'ヘ', 'べ':'ベ', 'ぺ':'ペ', 'ほ':'ホ', 'ぼ':'ボ', 'ぽ':'ポ',
        'ま':'マ', 'み':'ミ', 'む':'ム', 'め':'メ', 'も':'モ',
        'ゃ':'ャ', 'や':'ヤ', 'ゅ':'ュ', 'ゆ':'ユ', 'ょ':'ョ', 'よ':'ヨ',
        'ら':'ラ', 'り':'リ', 'る':'ル', 'れ':'レ', 'ろ':'ロ',
        'ゎ':'ヮ', 'わ':'ワ', 'ゐ':'ヰ', 'ゑ':'ヱ', 'を':'ヲ', 'ん':'ン', 'ゔ':'ヴ', 'ゕ':'ヵ', 'ゖ':'ヶ',
        }

ROMAON = {
        'ぁ': 'la', 'あ': 'a', 'ぃ': 'li', 'い': 'i', 'ぅ': 'lu', 'う': 'u', 'ぇ': 'le', 'え': 'e', 'ぉ': 'lo', 'お': 'o',
        'か': 'ka', 'が': 'ga', 'き': 'ki', 'ぎ': 'gi', 'く': 'ku', 'ぐ': 'gu', 'け': 'ke', 'げ': 'ge', 'こ': 'ko', 'ご': 'go',
        'さ': 'sa', 'ざ': 'za', 'し': 'shi', 'じ': 'ji', 'す': 'su', 'ず': 'zu', 'せ': 'se', 'ぜ': 'ze', 'そ': 'so', 'ぞ': 'zo',
        'た': 'ta', 'だ': 'da', 'ち': 'chi', 'ぢ': 'di', 'つ': 'tu', 'づ': 'du', 'て': 'te', 'で': 'de', 'と': 'to', 'ど': 'do',
        'な': 'na', 'に': 'ni', 'ぬ': 'nu', 'ね': 'ne', 'の': 'no',
        'は': 'ha', 'ば': 'ba', 'ぱ': 'pa', 'ひ': 'hi', 'び': 'bi', 'ぴ': 'pi', 'ふ': 'fu', 'ぶ': 'bu', 'ぷ': 'pu', 'へ': 'he', 'べ': 'be', 'ぺ': 'pe', 'ほ': 'ho', 'ぼ': 'bo', 'ぽ': 'po',
        'ま': 'ma', 'み': 'mi', 'む': 'mu', 'め': 'me', 'も': 'mo',
        'ゃ': 'lya', 'や': 'ya', 'ゅ': 'lyu', 'ゆ': 'yu', 'ょ': 'lyo', 'よ': 'yo',
        'ら': 'ra', 'り': 'ri', 'る': 'ru', 'れ': 're', 'ろ': 'ro',
        'ゎ': 'lwa', 'わ': 'wa', 'を': 'wo', 'ん': 'n', 'ゕ': 'lka', 'ゖ': 'lke',
        }

frequency_table = {}
word_frequency_table = {}

URL = 'https://www.edrdg.org/jmwsgi/srchres.py?s1=1&y1=1&t1={}&src=1&search=Search&svc=jmdict&sid=xxx'
TIMEOUT = httpx.Timeout(120.0, connect=120.0)

con = sqlite3.connect('./completion.db')
cur = con.cursor()

tm1 = time.perf_counter()

# cur.execute('delete from en_dict')
# with open('/usr/share/dict/en') as df:
#     for l in df.readlines():
#         if "'" not in l:
#             cur.execute("insert into en_dict values ('" + unidecode(l.rstrip().lower()) + "', '"+ l.rstrip() +"', 0, '/usr/share/dict/en');")
# print('en dict done!')

# cur.execute('delete from de_dict')
# with open('/usr/share/dict/ngerman') as df:
#     for l in df.readlines():
#         cur.execute("insert into de_dict values ('" + unidecode(l.rstrip().lower()) + "', '"+ l.rstrip() +"', 0, '/usr/share/dict/ngerman');")
# print('de dict done!')

# cur.execute('delete from esp_dict')
# with open('/usr/share/dict/esp') as df:
#     for l in df.readlines():
#         cur.execute("insert into esp_dict values ('" + unidecode(l.rstrip().lower()) + "', '"+ l.rstrip() +"', 0, '/usr/share/dict/esp');")
# print('esp dict done!')

with open('./frequency.txt') as fq:
    print('loading frequency...')
    for l in fq.readlines():
        kanji, frequency = l.rstrip().split(' ')
        frequency_table[kanji] = 5000/float(frequency)
    print('frequency table loaded!')

with open('./word-occurrence.txt') as wq:
    print('loading word frequency...')
    for l in wq.readlines():
        _, occurrence, word  = l.rstrip().split(' ')
        word_frequency_table[word] = occurrence
    print('word frequency table loaded!')

def parse_frequency(word:str) -> float:
    if word in word_frequency_table:
        return word_frequency_table[word]
    cnt_kanji, freq, gen = 0, 0, (ch for ch in word if ch in frequency_table)
    for ch in gen:
        freq += frequency_table[ch]
        cnt_kanji += 1
    return 0 if cnt_kanji == 0 else freq/cnt_kanji

def insert_sql(romaji, word, src):
    return "insert into jp_dict values('{}', '{}', 0, '{}', {})".format(romaji, word, src, parse_frequency(word))

cur.execute('drop table if exists jp_dict;')
cur.execute('drop table if exists jp_create_tmp;')

cur.execute('create table jp_dict (plain_text text, word text, chosen int, src text, frequency numeric);')
cur.execute('create index jp_idx on jp_dict (plain_text);')
cur.execute('create table jp_create_tmp (id integer primary key autoincrement, plain text, word text);')
print('table recreated!')

for kana, romaji in ROMAON.items():
    cur.execute(insert_sql(romaji, kana, 'romaji'))
print('romaji loaded')

print('loading from dict...')
with open('./edict-utf8.txt') as df:
    pat1 = re.compile(r'^.*\[.*\] /.*/$')
    pat2 = re.compile(r'^.* /.*/$')
    for l in track(df.readlines()):
        kana, romaji = '', ''
        try:
            if pat1.match(l.rstrip()):
                kanji = re.compile(r'^.*?(?<= )').findall(l)[0].rstrip()
                kana = re.compile(r'(?=\[).*?(?<=\])').findall(l)[0][1:-1]
                romaji = romkan.to_roma(kana).replace("'", '').replace('tsu', 'tu')
                cur.execute(insert_sql(romaji, kanji, 'edict-utf8.txt'))
            elif pat2.match(l.rstrip()):
                kana = re.compile(r'^.*?(?<= )').findall(l)[0].rstrip()
                romaji = romkan.to_roma(kana.replace('・', '')).replace("'", '').replace('tsu', 'tu')
                cur.execute(insert_sql(romaji, kana, 'edict-utf8.txt'))
        except:
            print(kana, romaji)

class MyHTMLParser(HTMLParser):
    kanji = ''
    def handle_starttag(self, tag, attrs):
        pass
    def handle_endtag(self, tag):
        pass
    def handle_data(self, data):
        # print("Encountered some data  :", data)
        if self.kanji == '':
            self.kanji = data
        elif data.rsplit() != '' and '･' in data:
            # print(self.kanji, romkan.to_roma(data.split('･')[0]))
            romaji = romkan.to_roma(data.split('･')[0]).replace('tsu', 'tu')
            cur.execute(insert_sql(romaji, self.kanji, 'kunnyomi'))


print('loading kunyomi...')
with open('./kunyomi.txt') as f:
    for l in track(f.readlines()):
        parser = MyHTMLParser()
        parser.feed(l)

con.commit()
print('jp dict done!')

tm2 = time.perf_counter()
print(f'Loading time elapsed: {tm2-tm1:0.2f} seconds.')
