#!/usr/bin/python3

import sys

[LEFT_BRACKET_SMALL, RIGHT_BRACKET_SMALL] = ['(', ')'] # ()
[LEFT_BRACKET_MIDDLE, RIGHT_BRACKET_MIDDLE] = ['[', ']'] # []
[LEFT_BRACKET_BIG, RIGHT_BRACKET_BIG] = ['{', '}'] # {}

def is_right_bracket(b):
    if b == RIGHT_BRACKET_SMALL or b == RIGHT_BRACKET_MIDDLE or b == RIGHT_BRACKET_BIG:
        return True
    return False

def is_left_bracket(b):
    if b == LEFT_BRACKET_SMALL or b == LEFT_BRACKET_MIDDLE or b == LEFT_BRACKET_BIG:
        return True
    return False

def match_brackets(left, right):
    if left == LEFT_BRACKET_SMALL and right == RIGHT_BRACKET_SMALL:
        return True
    if left == LEFT_BRACKET_MIDDLE and right == RIGHT_BRACKET_MIDDLE:
        return True
    if left == LEFT_BRACKET_BIG and right == RIGHT_BRACKET_BIG:
        return True
    return False

def get_right_by_left(left):
    if left == LEFT_BRACKET_SMALL:
        return RIGHT_BRACKET_SMALL
    if left == LEFT_BRACKET_MIDDLE:
        return RIGHT_BRACKET_MIDDLE
    if left == LEFT_BRACKET_BIG:
        return RIGHT_BRACKET_BIG

# assume start at next ch of left_bracket
def search_forward(s, start, left_bracket, right_bracket):
    [depth, end, idx] = [0, start, start]
    while idx < len(s):
        byte = s[idx]
        end += 1
        if byte == left_bracket:
            depth += 1
        elif byte == right_bracket and depth != 0:
            depth -= 1
        elif byte == right_bracket:
            return end-1
        idx += 1
    return start

def search_backward(s, start):
    if is_left_bracket(s[start]):
        return start
    immediate_rtn_when_stack_empty = True if is_right_bracket(s[start]) else False
    [stack, idx] = [[], start]
    while idx >= 0:
        if is_right_bracket(s[idx]): # put to stack
            stack.append(s[idx])
        elif is_left_bracket(s[idx]): # match
            if len(stack) == 0:
                return idx
            top = stack.pop()
            if match_brackets(s[idx], top) and len(stack) == 0 and immediate_rtn_when_stack_empty:
                return idx
        idx -= 1
    return None

def search_pair_brackets(s, col):
    start = search_backward(s, col)
    if start is None:
        return None
    bracket = s[start]
    end = search_forward(s, start+1, bracket, get_right_by_left(bracket))
    if end is None or end == start+1:
        return None
    return (start, end)


def search_next_pair_brackets(s, col):
    idx = col if not is_left_bracket(s[col]) else col+1
    while idx < len(s):
        if is_left_bracket(s[idx]):
            break
        idx += 1
    bracket = s[idx]
    end = search_forward(s, idx+1, bracket, get_right_by_left(bracket))
    if end is None or end == idx+1:
        return None
    return (idx, end)

def get_virtual_start_end(s, start, end, ts):
    vstart, vend, idx = 1, 1, 0
    for idx, ch in enumerate(s):
        if len(ch.encode('utf8')) == 3: # CJK character
            vstart += 1
        if ch == "\t":
            vstart += (ts - 1)
        vstart += 1
        if idx == start:
            break
    for idx, ch in enumerate(s):
        if len(ch.encode('utf8')) == 3: # CJK character
            vend += 1
        if ch == "\t":
            vend += (ts - 1)
        vend += 1
        if idx == end:
            break
    return (vstart-1, vend-1)


if __name__ == '__main__':
    [col, hex_str, ts] = sys.argv[1:]
    bs = bytearray.fromhex(hex_str).decode()
    start_end = search_pair_brackets(bs, int(col)-1) 
    if start_end is not None:
        start, end = start_end
        vstart, vend = get_virtual_start_end(bs, start, end, int(ts))
        print(vstart, vend, end='')
    # search next pair
    start_end = search_next_pair_brackets(bs, int(col)-1) 
    if start_end is not None:
        start, end = start_end
        vstart, vend = get_virtual_start_end(bs, start, end, int(ts))
        print('', vstart, vend, end='')

