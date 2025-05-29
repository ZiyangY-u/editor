#!/usr/bin/python3.8

import requests

HOME_URL = 'https://www.welt.de'

to_search = {}

class Target:
    def __init__(self, word:str, lb:bool, rb:bool, cs:bool):
        self.word = word
        self.lborder = lb
        self.rborder = rb
        self.case_sensitive = cs

def start_crawl(targets):
    global to_search
    response = requests.get(HOME_URL)

if __name__ == '__main__':
    targets = [
            ]
    start_crawl(targets)
