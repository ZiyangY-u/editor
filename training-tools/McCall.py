#!/usr/bin/python3

# 软件质量特性

import random

model = {
        '功能性' : {
            '适合性',
            '准确性',
            '互用性',
            '依从性',
            '安全性',
            },
        '可靠性' : {
            '成熟性',
            '容错性',
            '易恢复性',
            },
        '易使用性' : {
            '易理解性',
            '易学性',
            '易操作性',
            },
        '效率' : {
            '时间特性',
            '资源特性',
            },
        '可维护性' : {
            '易分析性',
            '易改变性',
            '稳定性',
            '易测试性',
            },
        '可移植性' : {
            '适应性',
            '易安装性',
            '一致性',
            '易替换性',
            },
        }

bigs = list(model.keys())
smalls = []
for k in bigs:
    smalls.extend(model[k])

# test_big = random.choice(bigs)

def include_test():
    test_big = random.choice(bigs) # 质量特性
    print(f'质量特性`{test_big}`|包含|子特性：')
    small = random.choice(list(model[test_big]))
    osmalls = []
    for k in (k for k in bigs if k != test_big):
        osmalls.extend(model[k])
    try:
        items = random.sample(osmalls, 3) # 选项
    except ValueError:
        items = random.sample(osmalls, 2) # 选项
    items.append(small)
    random.shuffle(items)
    for idx, item in enumerate(items, start=1):
        print(idx, item)
    _ = input()
    print('\n' + small)
    for item in (item for item in items if item != small):
        print(item + '->' + find_big_by_small(item))

def not_include_test():
    test_big = random.choice(bigs) # 质量特性
    print(f'质量特性`{test_big}`|不包含|子特性：')
    try:
        smalls = random.sample(list(model[test_big]), 3)
    except ValueError:
        smalls = random.sample(list(model[test_big]), 2)
    osmalls = []
    for k in (k for k in bigs if k != test_big):
        osmalls.extend(model[k])
    item = random.choice(osmalls) # 选项
    smalls.append(item)
    random.shuffle(smalls)
    for i, small in enumerate(smalls, start=1):
        print(i, small)
    _ = input()
    print('\n' + item + '->' + find_big_by_small(item))

def find_big_by_small(small):
    for k in bigs:
        if small in model[k]:
            return k
    return ''

type = random.randint(0, 1)

if type == 1:
    include_test()
else:
    not_include_test()
