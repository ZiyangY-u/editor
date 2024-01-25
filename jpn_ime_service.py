#!/usr/bin/python3

import re
import time
import sys

dictionary = {}

VOWELS = ['a', 'i', 'u', 'e', 'o']
UPPER_LETTER = {'b':'ｂ',
                'c':'ｃ',
                'd':'ｄ',
                'f':'ｆ',
                'g':'ｇ',
                'h':'ｈ',
                'j':'ｊ',
                'k':'ｋ',
                'l':'ｌ',
                'm':'ｍ',
                'p':'ｐ',
                'q':'ｑ',
                'r':'ｒ',
                's':'ｓ',
                't':'ｔ',
                'v':'ｖ',
                'w':'ｗ',
                'x':'ｘ',
                'y':'ｙ',
                'z':'ｚ',}
HIRAKANA = {
        'q': 'っ', 'ltu': 'っ',
        'la': 'ぁ', 'a': 'あ', 'li': 'ぃ', 'i': 'い', 'lu': 'ぅ', 'u': 'う', 'le': 'ぇ', 'e': 'え', 'lo': 'ぉ', 'o': 'お',
        'ka': 'か', 'ga': 'が', 'ki': 'き', 'gi': 'ぎ', 'ku': 'く', 'gu': 'ぐ', 'ke': 'け', 'ge': 'げ', 'ko': 'こ', 'go': 'ご',
        'sa': 'さ', 'za': 'ざ', 'shi': 'し', 'ji': 'じ', 'su': 'す', 'zu': 'ず', 'se': 'せ', 'ze': 'ぜ', 'so': 'そ', 'zo': 'ぞ',
        'ta': 'た', 'da': 'だ', 'chi': 'ち', 'di': 'ぢ', 'tu': 'つ', 'du': 'づ', 'te': 'て', 'de': 'で', 'to': 'と', 'do': 'ど',
        'na': 'な', 'ni': 'に', 'nu': 'ぬ', 'ne': 'ね', 'no': 'の',
        'ha': 'は', 'ba': 'ば', 'pa': 'ぱ', 'hi': 'ひ', 'bi': 'び', 'pi': 'ぴ', 'fu': 'ふ', 'bu': 'ぶ', 'pu': 'ぷ', 'he': 'へ', 'be': 'べ', 'pe': 'ぺ', 'ho': 'ほ', 'bo': 'ぼ', 'po': 'ぽ',
        'ma': 'ま', 'mi': 'み', 'mu': 'む', 'me': 'め', 'mo': 'も',
        'lya': 'ゃ', 'ya': 'や', 'lyu': 'ゅ', 'yu': 'ゆ', 'lyo': 'ょ', 'yo': 'よ',
        'ra': 'ら', 'ri': 'り', 'ru': 'る', 're': 'れ', 'ro': 'ろ',
        'lwa': 'ゎ', 'wa': 'わ', 'wo': 'を', 'n': 'ん', 'lka': 'ゕ', 'lke': 'ゖ',
        'kya': 'きゃ', 'kyu': 'きゅ', 'kyo': 'きょ',
        'gya': 'ぎゃ', 'gyu': 'ぎゅ', 'gyo': 'ぎょ',
        'sha': 'しゃ', 'shu': 'しゅ', 'sho': 'しょ',
        'ja': 'じゃ', 'ju': 'じゅ', 'jo': 'じょ',
        'cha': 'ちゃ', 'chu': 'ちゅ', 'cho': 'ちょ',
        'nya': 'にゃ', 'nyu': 'にゅ', 'nyo': 'にょ',
        'hya': 'ひゃ', 'hyu': 'ひゅ', 'hyo': 'ひょ',
        'mya': 'みゃ', 'myu': 'みゅ', 'myo': 'みょ',
        'rya': 'りゃ', 'ryu': 'りゅ', 'ryo': 'りょ',
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

def romaji_to_hirakana(romaji:str):
    kana_buf = ''
    romaji_buf = ''
    for ch in romaji:
        if ch in VOWELS:
            romaji_buf += ch
            if len(romaji_buf) > 2 and romaji_buf[0] not in VOWELS and romaji_buf[0] == romaji_buf[1]:
                if romaji_buf[0] == 'n':
                    kana_buf += HIRAKANA['n']
                    romaji_buf = romaji_buf[2:]
                else: # add っ
                    kana_buf += HIRAKANA['q']
                    romaji_buf = romaji_buf[1:]
            if romaji_buf in HIRAKANA:
                kana_buf += HIRAKANA[romaji_buf]
                romaji_buf = ''
            elif len(romaji_buf) == 3 and romaji_buf[0] == 'n' and romaji_buf[1:] in HIRAKANA:
                kana_buf += HIRAKANA['n']
                kana_buf += HIRAKANA[romaji_buf[1:]]
                romaji_buf = ''

        if ch not in VOWELS:
            romaji_buf += ch
    if len(romaji_buf) > 0:
        if romaji_buf == 'nn':
            kana_buf += HIRAKANA['n']
        # else:
        #     for ch in romaji_buf:
        #         if ch in UPPER_LETTER:
        #             kana_buf += UPPER_LETTER[ch]
    return kana_buf

# assert romaji_to_hirakana('a') == 'あ'
# assert romaji_to_hirakana('u') == 'う'
# assert romaji_to_hirakana('aiueo') == 'あいうえお'
# assert romaji_to_hirakana('lu') == 'ぅ'
# assert romaji_to_hirakana('lula') == 'ぅぁ'
# assert romaji_to_hirakana('ula') == 'うぁ'
# assert romaji_to_hirakana('lua') == 'ぅあ'
# assert romaji_to_hirakana('socchi') == 'そっち'
# assert romaji_to_hirakana('narerunoni') == 'なれるのに'
# assert romaji_to_hirakana('yappari') == 'やっぱり'
# assert romaji_to_hirakana('ryuunosuke') == 'りゅうのすけ'
# assert romaji_to_hirakana('lya') == 'ゃ'
# assert romaji_to_hirakana('sonnna') == 'そんな'
# assert romaji_to_hirakana('sonn') == 'そん'
# assert romaji_to_hirakana('seikyuusho') == 'せいきゅうしょ'

if __name__ == '__main__':
    # load()
    if sys.argv[1] == '-t': # translate
        print(romaji_to_hirakana(sys.argv[2]), end='')
