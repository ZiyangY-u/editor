#!/usr/bin/python3.8

import os
import time
import pyperclip
from os import access, R_OK
from os.path import isfile
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

folder_path = './articles'
driver_path = './geckodriver-v0.36.0-win64/geckodriver.exe'
skip_files = set()

MAX_SLEEP_TIME = 600

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


def auto_ai_answer(question_path):
    service = Service(driver_path)
    service = webdriver.FirefoxService(executable_path = driver_path)
    driver = webdriver.Firefox(service=service)

    driver.get('https://www.wenxiaobai.com/')
    print('start waiting input box')
    wait = WebDriverWait(driver, 180)
    input_box = wait.until(
            EC.presence_of_element_located((By.XPATH, '//textarea[@placeholder="给 小白 发送消息"]'))
            )
    if input_box:
        print('got input box')
    with open(question_path, mode='r', encoding='utf8') as f:
        content = f.read()
    pyperclip.copy(content)
    print('input content')
    input_box.send_keys(Keys.CONTROL + "v")
    print('enter')
    input_box.send_keys(Keys.ENTER)

    time.sleep(3)
    wait = WebDriverWait(driver, 2)
    try:
        sent = wait.until(
                # EC.presence_of_element_located((By.XPATH, '//*[local-name()="svg" and contains(@name, "new-send")]'))
                EC.presence_of_element_located((By.XPATH, '//*[local-name()="svg" and contains(@name, "send-normal-stop")]'))
                )
    except TimeoutException:
        skip_files.add(question_path)
        print(f'skip {question_path}')
        driver.quit()
        return

    wait = WebDriverWait(driver, 180)
    copy_btn = wait.until(
            # EC.presence_of_element_located((By.XPATH, '//*[local-name()="svg" and contains(@name, "new-send")]'))
            EC.presence_of_element_located((By.XPATH, '//*[local-name()="svg" and contains(@name, "chatbottomcopy")]'))
            )
    if copy_btn:
        print('done!')
        copy_btn.click()
        md_text = pyperclip.paste()
        with open(question_path.replace('.txt', '.md'), mode='w+', encoding='utf8') as f:
            f.write(md_text)
    driver.quit()

if __name__ == '__main__':
    # auto_ai_answer(f'{folder_path}/article-ansehen-article121548889.txt')
    sleep_time = 2
    while True:
        target_f = get_target()
        if target_f is None:
            sleep_time = sleep_time + 10 if sleep_time + 10 < MAX_SLEEP_TIME else MAX_SLEEP_TIME
        else:
            try:
                print(f'target: {target_f}')
                auto_ai_answer(target_f)
                sleep_time = 2
            except:
                pass
        print(f'sleep for {sleep_time} sec')
        time.sleep(sleep_time)
