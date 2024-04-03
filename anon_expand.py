#!/usr/bin/python3
import sys
import re
import subprocess

ESCAPE = {
        'a' : '[aäáAÄÁ]',
        'i' : '[iïíIÏÍ]',
        'u' : '[uüúUÜÚ]',
        'e' : '[eëéEËÉ]',
        'o' : '[oöóOÖÓ]',
        'n' : '[nñNÑ]',
        's' : '[sSß]',
        }

UPPER = {
        'ä':'Ä',
        'ï':'Ï',
        'ë':'Ë',
        'ü':'Ü',
        'ö':'Ö',
        'á':'Á',
        'í':'Í',
        'é':'É',
        'ú':'Ú',
        'ó':'Ó',
        }

def head_tail_expand(keyword:str, word:str, fmt:str):
    # keyword should will be removed from word and formatted into fmt
    if word.startswith(keyword):
        content = re.sub(r'^' + keyword, '', word)
        return fmt.format(content = content)
    if word.endswith(keyword):
        content = re.sub(keyword + r'$', '', word)
        return fmt.format(content = content)

def vim_expand(word:str):
    expand = ''

    expand = head_tail_expand('fu', word, 'fu! {content}()<cr>endf')
    if expand: return expand
    expand = head_tail_expand('hl', word, 'hi {content} cterm=bold ctermfg=$1 ctermbg=$2')
    if expand: return expand

    if word.startswith('if'): return 'if <cr>en'
    # if word.startswith('str'): return 'String'
    return ''

java_type = {
        's': 'String',
        'i': 'int',
        'I': 'Integer',
        'S': 'short',
        'd': 'double',
        'B': 'BigDecimal',
        'b': 'boolean',
        'v': 'var',
        }

def java_expand(word:str):
    expand = ''
    # p[r]ivate/p[u]blic/pr[o]tected [s]tatic [f]inal type
    if re.compile(r'[ruo]s?f?\w?').match(word): return java_variable(word)
    # tail G/S for GetXxxXxx/SetXxxXxx without ()
    if re.compile(r'.*G$').match(word): return 'get' + word[0].capitalize() + word[1:-1]
    if re.compile(r'.*S$').match(word): return 'set' + word[0].capitalize() + word[1:-1]
    if len(word) == 1 and word in java_type: return java_type[word]

    return expand

def java_variable(word:str):
    [scope, static, final, type] = ['public', None, None, '']
    if word.startswith('r'): scope = 'private'
    if word.startswith('o'): scope = 'protected'
    if re.compile(r'[ruo]sf?\w').match(word): static = 'static'
    if re.compile(r'[ruo]s?f\w').match(word): final = 'final'
    type = java_type[word[-1]]

    return ' '.join(filter(None, [scope, static, final, type]))

def sql_expand(word:str):
    if re.compile(r'sel\d*').match(word):
        return 'SELECT TOP ' + word[3:] + ' * from $1'
    if re.compile(r't\d*').match(word):
        return 'TOP ' + word[1:]
    return ''

def count_mark(word):
    cnt = 0
    for ch in word:
        if ch in UPPER:
            cnt += 1
    return cnt

def text_expand(word:str):
    exp = '^' + ''.join([ESCAPE[ch] if ch in ESCAPE else '['+ch+ch.upper()+']' for ch in word]) + '$'
    result = subprocess.run(['rg', exp, '-m5', '-I', '/usr/share/dict'], stdout=subprocess.PIPE)
    rst = result.stdout.decode('utf8').split('\n')
    rst_word = next(filter(lambda w: w!= word, sorted(rst, key=count_mark, reverse=True)), '') if rst else ''
    # from dictionary
    if rst_word:
        return rst_word
    return ''

def latex_expand(word:str):
    if re.compile(r'\dsq').match(word): # sqrt n
        return '\\sqrt[' + word[0] + ']{$0}'
    if re.compile(r'tria\w\w\w').match(word): # triangle
        return '\\bigtriangleup {}'.format(word[4:].upper())
    if re.compile(r'\w\wpp\w\w').match(word): # perpendicular
        return '{} \\bot {}'.format(word[:2].upper(), word[4:].upper())
    return ''

def css_expand(word:str):
    if re.compile(r'^[mp][trlb]\d*$').match(word): return margin_padding(word[0], word[1], word[2:])
    return ''

def margin_padding(mp, trlb, px):
    mp_dic = {'m': 'margin', 'p': 'padding'}
    direct_dic = { 't': 'Top', 'r': 'Right', 'l': 'Left', 'b': 'Bottom' }
    expand = mp_dic[mp] + direct_dic[trlb]
    return expand + (": '{px}px'".format(px=px) if px else ": '$1px'")

def common_expand(word:str):
    if re.compile(r'\w+_\w+').match(word): # snake to camel
        camel = ''.join(w.title() for w in word.split('_'))
        return camel[0].lower() + camel[1:]
    if re.compile(r'\w+[A-Z]\w+').match(word): # camel to snake
        return re.sub(r'(?<!^)(?=[A-Z])', '_', word).lower()
    if word == 'ret': return 'return'
    return ''

if __name__ == '__main__':
    [word, ft, reg] = ['', '', '']
    if len(sys.argv) > 1:
        word = sys.argv[1]
    if len(sys.argv) > 2:
        ft = sys.argv[2]
        
    expand = ''
    if word == '': 
        print('', end='')
    if ft == 'vim':
        expand = vim_expand(word)
    if ft == 'java':
        expand = java_expand(word)
    if ft == 'tex':
        expand = latex_expand(word)
    if ft == 'sql' or ft == 'xml':
        expand = sql_expand(word)
    if ft == 'text' or ft == 'ark':
        expand = text_expand(word)
    if ft == 'javascript' or ft == 'css' or ft == 'less':
        expand = css_expand(word)

    # if expand == '':
    #     expand = common_expand(word)

    print(expand, end='')
