#!/usr/bin/python3

import sys
from pair_hint import get_virtual_start_end

SINGLE = "'"
DOUBLE = '"'

def is_quote(ch):
    if ch == SINGLE or ch == DOUBLE:
        return True
    return False

# assume start at next ch of left_bracket
def search_forward(s, start, quote):
    [end, idx] = [start, start]
    while idx < len(s):
        end += 1
        if s[idx] == quote:
            return end - 1
        idx += 1
    return None

def search_pair_quotes(s, col):
    idx = col if not is_quote(s[col]) else col+1
    while idx >= 0:
        if idx < len(s) and is_quote(s[idx]):
            end = search_forward(s, idx+1, s[idx])
            if end is not None:
                return (idx, end)
        idx -= 1
    return None

def search_next_pair_quotes(s, col):
    idx = col if not is_quote(s[col]) else col+1
    while idx < len(s):
        if is_quote(s[idx]):
            break
        idx += 1
    quote = s[idx]
    end = search_forward(s, idx+1, quote)
    if end is None or end == idx+1:
        return None
    return (idx, end)

if __name__ == '__main__':
    [col, hex_str, ts] = sys.argv[1:]
    bs = bytearray.fromhex(hex_str).decode()
    start_end = search_pair_quotes(bs, int(col)-1) 
    if start_end is not None:
        start, end = start_end
        vstart, vend = get_virtual_start_end(bs, start, end, int(ts))
        print(vstart, vend, end='')
        # search next pair
        next_start_end = search_next_pair_quotes(bs, end+1) 
        if next_start_end is not None:
            start, end = next_start_end
            vstart, vend = get_virtual_start_end(bs, start, end, int(ts))
            print('', vstart, vend, end='')
    else:
        # search next pair
        next_start_end = search_next_pair_quotes(bs, int(col)-1) 
        if next_start_end is not None:
            start, end = next_start_end
            vstart, vend = get_virtual_start_end(bs, start, end, int(ts))
            print(vstart, vend, end='')
