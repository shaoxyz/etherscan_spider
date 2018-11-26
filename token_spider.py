# -*- coding:utf-8 -*-
# Python3
# File    : token_spider
# Time    : 2018/6/28 13:56
# Author  : Shaweb
from pprint import pprint

import requests

from bs4 import BeautifulSoup



def req_token_info(p):
    url = "https://etherscan.io/tokens?p={}".format(p)

    r = requests.get(url)

    soup = BeautifulSoup(r.text, 'lxml')

    tbody = soup.find('tbody')
    tds = tbody.find_all('td','hidden-xs')
    token_info = {}

    for i in tds:

        item = i.find('h5')
        if item == None:
            continue
        token_info[item.text] = item.find('a')['href'].replace('/token/','')
    return token_info



if __name__ == '__main__':
    import json
    tokens = {}
    for i in range(1,12):
        d = req_token_info(i)
        pprint(d)
        tokens.update(d)

    with open('token_info(backup).json', 'w+') as f:
        json.dump(tokens, f, indent=4)