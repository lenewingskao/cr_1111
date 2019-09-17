#!/usr/bin/env python
# coding: utf-8

import requests
import lxml
import json
from bs4 import BeautifulSoup
import threading
import time
import os

# connect mysql db
from cr_1111.myConnect import myConnect


# content parse
def getContent(url):

    #url = "https://www.1111.com.tw/job/91139337/"
    #url = "https://www.1111.com.tw/job/91147910/"
    #url = "https://www.1111.com.tw/job/91153365/"
    #url = "https://www.1111.com.tw/job/86026481/"

    jobno = url.split('/')[-2]
    res = requests.get(url)
    html = BeautifulSoup(res.text, 'lxml')

    # data dict
    saved = {}
    saved["jobno"] = jobno
    saved["joburl"] = url

    # 職稱
    logo = html.find("div", class_="logoTitle")
    if logo == None:
        saved["Oops"] = "已經結束徵才"
        return saved
        
    saved['title'] = logo.find("h1").text
    # 公司
    ellipsis = logo.find("li", class_="ellipsis")
    saved['corpid'] = ellipsis.find("a")["href"].split('/')[-2]
    saved['corpname'] = ellipsis.text

    incontent = html.find("section", id="incontent")
    # 更新日期
    update = incontent.find("span", class_="update")
    ds = update.find_all("div")
    for d in ds:
        d.extract()
    saved['update'] = update.text.replace('更新日期：','')

    # 工作內容
    cont1 = {}
    workcont = incontent.find("ul", class_="dataList")
    try:
        cont1['description'] = workcont.find("li", class_="paddingLB").text
    except:
        pass

    wcontLis = workcont.find_all("li")
    for li in wcontLis:
        try:
            lli = li.find_all("div")
            lliname = lli[0].text.replace('：','')
            ds = lli[1].find_all("div", class_="cateshow")
            for d in ds:
                d.extract()
            ds = lli[1].find_all("a")
            for d in ds:
                d.extract()
            cont1[lliname] = (lli[1].text.replace(' ','')).replace('　','')
        except:
            pass
    saved['工作內容'] = cont1

    # 工作福利
    try:
        cont2 = {}
        welfare = workcont.find("div", class_="wrap").find_all("p", class_="contxt")
        for wf in welfare:
            try:
                wspan = wf.find("span").text
                cont2[wspan] = wf.text.replace(wspan,"").strip()
            except:
                pass
        saved['工作福利'] = cont2
    except:
        pass

    # 工作條件
    cont3 = {}
    condi = incontent.find("article", class_="boxsize")
    wcondiLis = condi.find_all("li")
    for li in wcondiLis:
        try:
            lli = li.find_all("div")
            lliname = lli[0].text.replace('：','')

            cont3[lliname] = lli[1].text.strip()
        except:
            pass
    saved['要求條件'] = cont3
    
    # 應徵人數
    eurl = "https://www.1111.com.tw/includesU/employeeShowRecruits.asp"
    datas = {'eNo': jobno}
    eres = requests.post(eurl, data = datas)
    eres.encoding = 'utf-8'
    r = BeautifulSoup(eres.text, 'lxml')
    saved['intern'] = r.find_all("span")[-1].text
    
    # print(saved)
    return saved


# thread work
def mThread(duty):
    # Each worker thread can have own connection.
    db = myConnect()

    # 儲存路徑
    spath = "jobcontent/" + duty + "/"
    if not os.path.exists(spath):
        os.makedirs(spath)

    cnt = 1
    seq = 1
    contents = []
    
    sql = "select distinct jburl from joblist1111 where did='%s' "
    rs = db.query(sql % duty)
    for jburl in rs:
        # 200筆存成一個json, filename = 業務類別-序號
        if cnt > 200:
            sfile = duty + "-" + str(seq) + ".json"
            fp = open(spath + sfile, "w", encoding="utf-8")
            json.dump(contents, fp)
            fp.close()
            contents = []
            cnt = 1
            seq += 1

        print(duty, jburl[0])
        work = getContent(jburl[0])
        if work:
            contents.append(work)
        cnt += 1

    # 最後不足200的存檔
    sfile = duty + "-" + str(seq) + ".json"
    fp = open(spath + sfile, "w", encoding="utf-8")
    json.dump(contents, fp)
    fp.close()

    db.close()


if __name__ == "__main__":
    tStart = time.time()#計時開始
    start = time.strftime("%m-%d %H:%M:%S")

    db = myConnect()
    # testd = '150100' testd = '250300'  testd = '120200'
    #testd = '250200'
    #sql = "select did from duty1111 where level=1 and did='%s'" % testd
    sql = "select did from duty1111 where level=1"
    dutys = db.query(sql)
    db.close()

    threadList = list()
    for duty in dutys:
        threadList.append(threading.Thread(target=mThread, args=(duty)))

    for i in threadList:
        i.start()
        # time.sleep(0.1)
    for i in threadList:
        i.join()


    tEnd = time.time()#計時結束
    end = time.strftime("%m-%d %H:%M:%S")
    print('done!! 花費:', (tEnd - tStart), 'sec')
    print(start, ' ~ ', end)
