#!/usr/bin/env python
# coding: utf-8

import requests
import lxml
from bs4 import BeautifulSoup
import time


# connect mysql db
from cr_1111.myConnect import myConnect
db = myConnect()

# 先清空duty1111
db.execmmit("TRUNCATE TABLE duty1111")


def mWork(url,level,tdid=''):
    res = requests.get(url)
    html = BeautifulSoup(res.text, 'lxml')
    dutyList = html.find("div", class_="dutyList")
    dutys = dutyList.find_all("a")
    params = []
    for d in dutys:
        dd = d["href"].split('&')
        did = ''
        for item in dd:
            if 'd=' in item:
                did = item.replace('d=','')
        if did != '':
            if tdid != '' and did == tdid:
                continue
            else:
                print(d.text, did, level)
                params.append((did, d.text, level))
    return params


sql = "insert into duty1111 values (%s,%s,%s)"

#level1
url = "https://www.1111.com.tw/job-bank/category.asp?cat=1"
params = mWork(url, 1)
if params:
    db.executemany(sql, params)

#level2
rs = db.query("select did from duty1111")
for did in rs:
    url = "https://www.1111.com.tw/job-bank/category.asp?cat=1&d="+did[0]
    params = mWork(url, 2, did[0])
    if params:
        db.executemany(sql, params)

db.close()
print('done!!')
