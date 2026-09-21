#!/usr/bin/python3

from xpinyin import Pinyin
import sys
import bisect

p = Pinyin()

param = sys.argv[1]
# print(param)

file_path = sys.argv[2]

# 匹配字符的高亮颜色，可按喜好修改，例如：
#   '\033[1;31m' 粗体红    '\033[1;33m' 粗体黄
#   '\033[38;5;208m' 256色橙
COLOR_MATCH = '\033[1;31m'
COLOR_RESET = '\033[0m'

# 中文（拼音首字母）命中的加分权重：同样紧凑的匹配下，命中的中文越多排越前。
# 例如 rkd：入库单(R-K-D) 全中文 → 密度1.0 + 0.5；markdown 中 r-k-d 同样连续
# 但全是英文 → 只剩密度1.0，于是入库单排在前面
CJK_BONUS = 0.5

'''
"通过python判断一个字符串A中的每个..."点击查看元宝的回答
https://yb.tencent.com/s/fadMDUeCEoCn
'''

def build_initials(line):
    # 返回 [(首字母, 行内下标, 是否中文), ...]，拼接结果与 ''.join(p.get_initials(line)) 一致，
    # 但额外记录了每个首字母来自行内哪个字符、该字符是否为中文
    pairs = []
    for idx, ch in enumerate(line):
        for c in p.get_initials(ch):
            pairs.append((c.upper(), idx, '一' <= ch <= '鿿'))
    return pairs

def find_best_match(A, pairs):
    # 在首字母序列中找最紧凑的子序列匹配（与原 calculate_density 算法一致），
    # 并按中文命中占比加分（CJK_BONUS），使同样连续的中文词排在英文词前面
    # 返回 (得分, pairs 下标列表)；无匹配时返回 (0.0, None)
    if not A:
        return 1.0, []
    char_positions = {}
    for i, (char, _, _) in enumerate(pairs):
        if char not in char_positions:
            char_positions[char] = []
        char_positions[char].append(i)

    best_span = float('inf')
    best_pos = None
    first_char = A[0]
    if first_char not in char_positions:
        return 0.0, None

    # 枚举A[0]在B中的所有位置
    for start_idx in char_positions[first_char]:
        current_pos = start_idx
        matched = [start_idx]
        valid = True
        for char in A[1:]:
            if char not in char_positions:
                valid = False
                break
            positions = char_positions[char]
            # 二分查找第一个大于current_pos的位置
            i = bisect.bisect_right(positions, current_pos)
            if i >= len(positions):
                valid = False
                break
            current_pos = positions[i]
            matched.append(current_pos)

        if valid:
            span = current_pos - start_idx + 1
            if span < best_span:
                best_span = span
                best_pos = matched

    if best_pos is None:
        return 0.0, None
    density = len(A) / best_span
    cjk_ratio = sum(1 for i in best_pos if pairs[i][2]) / len(A)
    return density + CJK_BONUS * cjk_ratio, best_pos

def highlight(content, pairs, matched):
    # 在匹配到的字符两侧插入 ANSI 颜色码（从后往前插，避免下标失效）
    for i in reversed(matched):
        col = pairs[i][1]
        content = content[:col] + COLOR_MATCH + content[col] + COLOR_RESET + content[col+1:]
    return content

rst = []
with open(file_path, 'r', encoding='utf8') as f:
    for ln, line in enumerate(f, start=1):
        # strip 后再做匹配，保证下标与最终输出内容一致
        content = line.strip()
        pairs = build_initials(content)
        density, matched = find_best_match(param.upper(), pairs)
        if density > 0:
            rst.append({'info': f'{file_path}:{ln}:{highlight(content, pairs, matched)}', 'density':density})

for info in sorted(rst, key=lambda x : x['density'], reverse=True):
    print(info['info'])
