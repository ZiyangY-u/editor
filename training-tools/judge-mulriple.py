#!/usr/bin/python3

# 给定一个正整数，判断它的因数有哪些
# 一个数能被2(或5)整除，当且仅当其末一位能被2(或5)整除      10
# 一个数能被4(或25)整除，当且仅当其末两位能被4(或25)整除    100
# 一个数能被8(或125)整除，当且仅当其末三位能被8(或1275)整除 1000

# 一个数能被3整除，当且仅当其各个位数字之和能被3整除
# 一个数能被9整除，当且仅当其各个位数字之和能被9整除

# 一个数能被7整除，当且仅当其末一位数的两倍，与剩下的数之差为7的倍数 (n <= 999)
# 一个数能被7整除，当且仅当其末三位数，与剩下的数之差为7的倍数 (n > 999)

# 一个数是11的倍数，当且仅当其奇数位之和与偶数位之和的差为11的倍数

import random
import time

flag = random.randint(0, 1)
if flag == 0:
    random_num = random.randint(2, 99999)
else:
    random_num = random.randint(2, 999)

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
