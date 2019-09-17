#!/usr/bin/env python
# coding: utf-8

import requests
import lxml
from bs4 import BeautifulSoup
import threading
import time


# connect mysql db
from cr_1111.myConnect import myConnect
db = myConnect()

# 先清空joblist1111
db.execmmit("TRUNCATE TABLE joblist1111")


def jlThread(duty):
    # Each worker thread can have own connection.
    db = myConnect()

    # ps=200
    url = "https://www.1111.com.tw/job-bank/job-index.asp?ss=s&tt=1&d0="+ duty +"&si=1&ps=200&page=1"
    res = requests.get(url)
    html = BeautifulSoup(res.text, 'lxml')
    # get total pages
    pagedata = html.find("div", class_="pagedata")
    totpage = int(pagedata.text.split('頁')[0].split('/')[1].strip())
    # get joblist
    for page in range(1, totpage + 1):
        newurl = url.replace('page=1', 'page='+str(page))
        print(newurl)
        res = requests.get(newurl)
        html = BeautifulSoup(res.text, 'lxml')
        jbInfos = html.find("div", id="jobResult").find_all("div", class_="jbInfoin")
        params = []
        for jb in jbInfos:
            agroup = jb.find_all("a")
            title = agroup[0]["title"]
            jburl = "https:" + agroup[0]["href"]
            corp = agroup[1].text
            courl = "https:" + agroup[1]["href"]

            # jburl不重複insert
            q_jburl = db.queryone("select jburl from joblist1111 where jburl='%s'" % jburl)
            if q_jburl is None:
                params.append((duty,title,jburl,corp,courl))
            
        #一頁commit
        sql = "insert into joblist1111 (did,title,jburl,corp,courl,crdate) values (%s,%s,%s,%s,%s,SYSDATE())"
        if params:
            db.executemany(sql, params)

    db.close()


if __name__ == "__main__":
    tStart = time.time()#計時開始
    start = time.strftime("m-%d %H:%M:%S")

    # read duty
    # test :　where did in ('250100','250300')
    sql = "select did from duty1111 where level=1"
    rs = db.query(sql)
    threadList = list()
    for duty in rs:

        threadList.append(threading.Thread(target=jlThread, args=(duty)))

    for i in threadList:
        i.start()
        # time.sleep(0.1)
    for i in threadList:
        i.join()

    # close mysql connect
    db.close()

    tEnd = time.time()  # 計時結束
    end = time.strftime("m-%d %H:%M:%S")
    print('done!! 花費:', (tEnd - tStart), 'sec')
    print(start, ' ~ ', end)
