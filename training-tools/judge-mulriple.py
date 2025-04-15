#!/usr/bin/python3

# 给定一个正整数，判断它的因数有哪些
# 一个数能被2(或5)整除，当且仅当其末一位能被2(或5)整除      10
# 一个数能被4(或25)整除，当且仅当其末两位能被4(或25)整除    100
# 一个数能被8(或125)整除，当且仅当其末三位能被8(或1275)整除 1000

# 一个数能被3整除，当且仅当其各个位数字之和能被3整除
# 一个数能被9整除，当且仅当其各个位数字之和能被9整除

# https://www.bilibili.com/opus/562149075171891389
# 一个数能被7整除，当且仅当其末一位数的两倍，与剩下的数之差为7的倍数 (n <= 999)
# 一个数能被7整除，当且仅当其末三位数，与剩下的数之差为7的倍数 (n > 999)

# 一个数是11的倍数，当且仅当其奇数位之和与偶数位之和的差为11的倍数

# 一个数是13的倍数，去掉末位后余下的部分加上末位的4倍，结果是13的倍数
# 7293
# 729 + 3 * 4 = 741
# 74 + 1 * 4 = 78
# 7 + 8 * 4 = 39
# 13 ,26 ,39 ,52 ,65 ,78 ,91

# 如果一个数去掉末位后余下的数减去末位的5倍，结果是17的倍数，那么原来的数就是17的倍数
# 6137
# 613 - 7 * 5 = 578
# 57 - 8 * 5 = 17
# 17 ,34 ,51 ,68 ,85

import random
import time

while True:
    factor2 = random.uniform(0, 1)
    factor3 = random.uniform(0, 1)
    factor4 = random.uniform(0, 1)
    factor5 = random.uniform(0, 1)
    factor7 = random.uniform(0, 1)
    factor8 = random.uniform(0, 1)
    factor9 = random.uniform(0, 1)
    factor11 = random.uniform(0, 1)
    factor13 = random.uniform(0, 1)
    factor17 = random.uniform(0, 1)
    if factor2 + factor3 + factor4 + factor5 + factor7 + factor8 + factor9 + factor11 + factor13 + factor17 > 0:
        break


def include_factors(n):
    if factor2 == 1 and n % 2 != 0:
        return False
    if factor3 == 1 and n % 3 != 0:
        return False
    if factor4 == 1 and n % 4 != 0:
        return False
    if factor5 == 1 and n % 5 != 0:
        return False
    if factor7 == 1 and n % 7 != 0:
        return False
    if factor8 == 1 and n % 8 != 0:
        return False
    if factor9 == 1 and n % 9 != 0:
        return False
    if factor11 == 1 and n % 11 != 0:
        return False
    if factor13 == 1 and n % 13 != 0:
        return False
    if factor17 == 1 and n % 17 != 0:
        return False
    return True

# flag = random.randint(0, 1)
flag = 0
while True:
    random_num = random.randint(2, 99999 if flag == 9 else 999)
    if include_factors(random_num):
        break

print(random_num)
t1 = time.time()

factors = input().split()
t2 = time.time()
for f in factors:
    print(f'{random_num} % {f} = {random_num % int(f)}')

print('---------- all factors ----------')
for i in range(2, random_num):
    if random_num % i == 0:
        print(f'{random_num} % {i} = {random_num % i}')

print('{t:.2f} sec used'.format(t = (t2 - t1)))
