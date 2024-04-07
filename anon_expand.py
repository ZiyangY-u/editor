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

def disp_pt(pt:str) -> str:
    pt_disp = pt[0] # first character
    n = re.findall(r'\d+', pt)
    if len(n) > 0:
        pt_disp += ('_' + n[0])
    if '-' in pt or "'" in pt:
        pt_disp += "'"
    return pt_disp

def get_pts(pts_str:str) -> list:
    pts = re.findall(r'\w\d?-?', pts_str)
    rst = []
    for pt in pts:
        rst.append(pt.upper().replace("-", "'"))
    return rst

def latex_expand(word:str):
    if re.compile(r'\dsq').match(word): # sqrt n
        return '\\sqrt[' + word[0] + ']{$0}'
    if re.compile(r'tri\w\d?-?\w\d?-?\w\d?-?').match(word): # triangle
        pts = get_pts(word[3:])
        return '\\bigtriangleup {}'.format(''.join([disp_pt(pt) for pt in pts]))
    if re.compile(r'\w\d?-?\w\d?-?pp\w\d?-?\w\d?-?').match(word): # perpendicular
        pts = get_pts(word.replace('pp', ''))
        return '{}{} \\bot {}{}'.format(disp_pt(pts[0]), disp_pt(pts[1]), disp_pt(pts[2]), disp_pt(pts[3]))
    if re.compile(r'\w\d?-?\w\d?-?pl\w\d?-?\w\d?-?').match(word): # parallel
        pts = get_pts(word.replace('pl', ''))
        return '{}{} \\parallel {}{}'.format(disp_pt(pts[0]), disp_pt(pts[1]), disp_pt(pts[2]), disp_pt(pts[3]))
    if word.startswith('pt'): # define and draw point
        pts = get_pts(word[2:])
        pt = pts[0]
        return f"% define pt {pt}.<CR>" \
                + "\\tkzDefPoint($0){" + pt + "}<CR>" \
                + "\\tkzLabelPoint[ ]("+ pt +"){$"+ disp_pt(pt) + "$}<CR>" \
                + "\\tkzDrawPoint[fill=black](" + pt + ")"
    if word.startswith('ln'): # define and draw line by tkz-euclide
        pts = get_pts(word[2:])
        [pt1, pt2] = [pts[0], pts[1]]
        return f'% draw line {pt1}-{pt2}<CR>' \
                + '\\tkzDrawLine[add= 0.0 and 0.0]({}, {})'.format(pt1, pt2)
    if re.compile(r'll.*').match(word): # line and line intercept
        pts = get_pts(word[2:])
        if len(pts) == 5:
            [pt1, pt2, pt3, pt4, pt5] = [pts[0], pts[1], pts[2], pts[3], pts[4]]
            return f"% intercepts line {pt1}-{pt2}, line {pt3}-{pt4}, intercepts at {pt5}.<CR>" \
                    + f"\\tkzInterLL({pt1},{pt2})({pt3},{pt4})<CR>" \
                    + "\\tkzGetPoint{" + pt5 + "}<CR>" \
                    + f"\\tkzLabelPoint[ ]({pt5})" + "{$" + disp_pt(pt5) + "$}<CR>" \
                    + f"\\tkzDrawPoint[fill=black]({pt5}) % line-line intercept end<CR>"
    if word.startswith('pol'): # point on line
        pts = get_pts(word[3:])
        if len(pts) == 3:
            [pt1, pt2, pt3] = [pts[0], pts[1], pts[2]]
            return f'% define pt {pt3} on line {pt1}-{pt2}<CR>' \
                    + f'\\tkzDefPointOnLine[pos=0.5$0]({pt1}, {pt2})<CR>' \
                    + '\\tkzGetPoint{' + pt3 + '}<CR>' \
                    + f"\\tkzLabelPoint[ ]({pt3})" + "{$" + disp_pt(pt3) + "$}<CR>" \
                    + f"\\tkzDrawPoint[fill=black]({pt3}) % point of line end<CR>"
    if word.startswith('pp'): # project(perpendicular) point to line
        pts = get_pts(word[2:])
        if len(pts) == 4:
            [pt1, pt2, pt3, pt4] = [pts[0], pts[1], pts[2], pts[3]]
            return f'% project pt pt1 onto line pt2-pt3 intercept at pt pt4.<CR>' \
                    + f'\\tkzDefPointBy[projection=onto {pt2}--{pt3}]({pt1})<CR>' \
                    + '\\tkzGetPoint{' + pt4 + '}<CR>' \
                    + f"\\tkzLabelPoint[ ]({pt4})" + "{$" + disp_pt(pt4) + "$}<CR>" \
                    + f"\\tkzDrawPoint[fill=black]({pt4})<CR>" \
                    + f'\\tkzDrawLine[add= 0.0 and 0.0]({pt1},{pt4}) % project end'
    if word.startswith('pl'): # parallel
        pts = get_pts(word[2:])
        if len(pts) == 4:
            [pt1, pt2, pt3, pt4] = [pts[0], pts[1], pts[2], pts[3]]
            return f'% from {pt1} parallel to line {pt2}-{pt3} go to pt {pt4}.<CR>' \
                    + f'\\tkzDefPointWith[colinear=at {pt1}]({pt2},{pt3})<CR>'\
                    + '\\tkzGetPoint{' + pt4 + '}<CR>' \
                    + f"\\tkzLabelPoint[ ]({pt4})" + "{$" + disp_pt(pt4) + "$}<CR>" \
                    + f"\\tkzDrawPoint[fill=black]({pt4})<CR>" \
                    + f'\\tkzDrawLine[add= 0.0 and 0.0]({pt1},{pt4}) % parallel end'
    if word.startswith('init'): # init coordinates
        n = re.findall(r'\d+', word)
        size = n[0] if len(n) == 1 else '5'
        return f'\\tkzInit[xmax={size},ymax={size},xmin=-{size},ymin=-{size}]<CR>' \
                + '\\tkzDrawX[>=latex]<CR>\\tkzDrawY[>=latex]<CR>' \
                + '\\tkzGrid<CR>\\tkzClip[space=1]'


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
