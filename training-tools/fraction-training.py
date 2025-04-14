#!/usr/bin/python3

# 资料分析除乘互换

import numpy as np
import time

mean = 7
std_dev = 10

random_numbers = np.random.normal(loc=mean, scale=std_dev, size=1)
test = round(abs(random_numbers[0]), 2)

print(test)
t1 = time.time()
answer = float(input())
t2 = time.time()
print('multiplied:', test * answer)
print('{t:.2f} sec used'.format(t = (t2 - t1)))
