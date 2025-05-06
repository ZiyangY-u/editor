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
    print(f'质量特性`{test_big}`包含子特性：')
    small = random.choice(list(model[test_big]))
    osmalls = []
    for k in (k for k in bigs if k != test_big):
        osmalls.extend(model[k])
    items = random.sample(osmalls, 3) # 选项
    items.append(small)
    rst = random.shuffle(items)
    for i in items:
        print(i)
    _ = input()
    print('\n' + small)

def not_include_test():
    test_big = random.choice(bigs) # 质量特性
    print(f'质量特性`{test_big}`不包含子特性：')
    smalls = random.sample(list(model[test_big]), 3)
    osmalls = []
    for k in (k for k in bigs if k != test_big):
        osmalls.extend(model[k])
    item = random.choice(osmalls) # 选项
    smalls.append(item)
    rst = random.shuffle(smalls)
    for i in smalls:
        print(i)
    _ = input()
    print('\n' + item)


type = random.randint(0, 1)

if type == 1:
    include_test()
else:
    not_include_test()
