#!/usr/bin/python3

from xpinyin import Pinyin
import sys
import bisect

p = Pinyin()

param = sys.argv[1]
# print(param)

file_path = sys.argv[2]

'''
"通过python判断一个字符串A中的每个..."点击查看元宝的回答
https://yb.tencent.com/s/fadMDUeCEoCn
'''

def is_subsequence(A, B):
    i = 0
    n = len(A)
    if n == 0:
        return True
    for char in B:
        if i < n and char == A[i]:
            i += 1
            if i == n:
                break
    return i == n

def calculate_density(A, B):
    if not A:
        return 1.0
    if not is_subsequence(A, B):
        return 0.0

    # 构建字符位置映射
    char_positions = {}
    for idx, char in enumerate(B):
        if char not in char_positions:
            char_positions[char] = []
        char_positions[char].append(idx)

    min_span = float('inf')
    first_char = A[0]
    if first_char not in char_positions:
        return 0.0

    # 枚举A[0]在B中的所有位置
    for start_idx in char_positions[first_char]:
        current_pos = start_idx
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

        if valid:
            span = current_pos - start_idx + 1
            if span < min_span:
                min_span = span

    if min_span == float('inf'):
        return 0.0
    return len(A) / min_span


rst = []
with open(file_path, 'r', encoding='utf8') as f:
    for ln, line in enumerate(f, start=1):
        density = calculate_density(param.upper(), ''.join(p.get_initials(line)))
        if density > 0:
            rst.append({'info': f'{file_path}:{ln}:{line.strip()}', 'density':density})

for info in sorted(rst, key=lambda x : x['density'], reverse=True):
    print(info['info'])
