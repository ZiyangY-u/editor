#!/usr/bin/python3.8

import os
import time
import pyperclip
import shutil
from os import access, R_OK
from os.path import isfile
from selenium import webdriver
from selenium.webdriver import firefox
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime

one_drive_path = 'C:\\Users\\fvdi0046\\OneDrive2\\OneDrive\\articles'
folder_path = './articles'
firefox_driver_path = './geckodriver-v0.36.0-win64/geckodriver.exe'
edge_driver_path = './edgedriver_win64/msedgedriver.exe'

MAX_SLEEP_TIME = 600
REFRESH_CNT = 2

F_ROLE = 0
fservice = webdriver.FirefoxService(executable_path = firefox_driver_path)
firefox = webdriver.Firefox(service=fservice)
f_refresh_cnt = REFRESH_CNT

E_ROLE = 1
eservice = webdriver.EdgeService(executable_path = edge_driver_path)
options = webdriver.EdgeOptions()
options.add_argument("--window-size=1324,768")
edge = webdriver.Edge(service=eservice, options=options)
e_refresh_cnt = REFRESH_CNT

sleep_time = 2
skip_files = set()

def file_accessable(path):
    if isfile(path) and access(path, R_OK):
        return True
    return False

def get_target():
    for filename in os.listdir(folder_path):
        if filename.startswith('article-') and filename.endswith('.txt') \
                and not file_accessable(f'{folder_path}/{filename.replace(".txt", ".md")}') \
                and f'{folder_path}/{filename}' not in skip_files:
            return f'{folder_path}/{filename}'
    return None

def reopen(role):
    if role == F_ROLE:
        global firefox
        firefox.quit()
        firefox = webdriver.Firefox(service=fservice)
        init(firefox)
        f_refresh_cnt = REFRESH_CNT
    if role == E_ROLE:
        global edge
        edge.quit()
        edge = webdriver.Edge(service=eservice, options=options)
        init(edge)
        e_refresh_cnt = REFRESH_CNT

def init(driver):
    driver.get('https://www.wenxiaobai.com/?chatMode=temp')

def auto_ai_answer(driver, role, question_path):
    wait = WebDriverWait(driver, 3)
    new_dialog = wait.until(EC.presence_of_element_located((By.XPATH, '//*[local-name()="svg" and contains(@name, "chat-new")]')))
    new_dialog.click()
    time.sleep(2)

    print('waiting\r', end='')
    wait = WebDriverWait(driver, 180)
    input_box = wait.until(
            EC.presence_of_element_located((By.XPATH, '//textarea[@placeholder="给 小白 发送消息"]'))
            )
    if input_box:
        print('waiting got\r', end='')
    with open(question_path, mode='r', encoding='utf8') as f:
        content = f.read()
    pyperclip.copy(content)
    print('waiting got input\r', end='')
    input_box.send_keys(Keys.CONTROL + "v")
    print('waiting got input enter')
    input_box.send_keys(Keys.ENTER)

    time.sleep(3)
    wait = WebDriverWait(driver, 2)
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(string(), "去登录")]')))
        reopen(role)
    except TimeoutException:
        pass

    try:
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[local-name()="svg" and contains(@name, "send-normal-stop")]')))
    except TimeoutException:
        skip_files.add(question_path)
        print(f'skip {question_path}')
        init(driver)
        return

    wait = WebDriverWait(driver, 180)
    copy_btn = wait.until(EC.presence_of_element_located((By.XPATH, '//*[local-name()="svg" and contains(@name, "chatbottomcopy")]')))
    if copy_btn:
        print('done!')
        copy_btn.click()
        md_text = pyperclip.paste()
        target_file = question_path.replace('.txt', '.md')
        with open(target_file, mode='w+', encoding='utf8') as f:
            f.write(md_text)
        fname = target_file.split('/')[-1]
        one_drive_target_path = one_drive_path + '\\' + datetime.now().strftime("%Y%m%d")
        if not os.path.exists(one_drive_target_path):
            os.makedirs(one_drive_target_path)
        shutil.copyfile(target_file, f'{one_drive_target_path}\\{fname}')

if __name__ == '__main__':
    init(edge)
    init(firefox)
    cnt = 0

    while True:
        target_f = get_target()
        if target_f is None:
            sleep_time = sleep_time + 10 if sleep_time + 10 < MAX_SLEEP_TIME else MAX_SLEEP_TIME
        else:
            try:
                print(f'target: {target_f}')
                role = cnt % 2 # firefox, edge
                tm1 = time.perf_counter()

                if role == F_ROLE: # firefox
                    auto_ai_answer(firefox, F_ROLE, target_f)
                    f_refresh_cnt -= 1
                if role == E_ROLE: # edge
                    auto_ai_answer(edge, E_ROLE, target_f)
                    e_refresh_cnt -= 1

                tm2 = time.perf_counter()
                print(f'{tm2-tm1:0.2f} sec used')
                sleep_time = 2
            except:
                init(firefox)
                init(edge)

        if f_refresh_cnt == 0:
            reopen(F_ROLE)
        if e_refresh_cnt == 0:
            reopen(E_ROLE)
        print(f'sleep for {sleep_time} sec')
        time.sleep(sleep_time)
        cnt += 1
