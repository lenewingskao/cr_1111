import requests
import lxml
import json
from bs4 import BeautifulSoup
import threading
import time
import os

# connect mysql db
from cr_1111.myConnect import myConnect


def getContent(url):
    cont = {}
    try:
        res = requests.get(url)
        html = BeautifulSoup(res.text, 'lxml')
        cont['公司網址'] = url
        dataList = html.find("ul", class_="dataList")
        cont['公司名稱'] = dataList.find("li", class_="posR").text.strip()
        base = dataList.find_all("li")
        for li in base:
            try:
                lli = li.find_all("div")
                lliname = lli[0].text.replace('：', '')
                ds = lli[1].find_all("a", id="showmap")
                for d in ds:
                    d.extract()
                # print(lliname, lli[1].text)
                cont[lliname] = (lli[1].text.replace(' ', '')).replace('　', '')
            except:
                pass

        cont['公司介紹'] = html.find("p", class_="datainfo").text.strip()
        cont['產品服務'] = html.find("div", class_="product").find("p", class_="contxt").text.strip()
        # 工作福利
        try:
            cont2 = {}
            welfare = html.find("div", class_="benefit").find("div", class_="wrap").find_all("p", class_="contxt")
            for wf in welfare:
                try:
                    wspan = wf.find("span").text
                    cont2[wspan] = wf.text.replace(wspan, "").strip()
                except:
                    pass
            cont['工作福利'] = cont2
        except:
            pass
    except:
        pass

    return cont


if __name__ == "__main__":
    tStart = time.time()#計時開始
    start = time.strftime("%m-%d %H:%M:%S")

    db = myConnect()
    sql = "select distinct courl from joblist1111 "
    co_urls = db.query(sql)
    db.close()

    # 儲存路徑
    spath = "corps/"
    if not os.path.exists(spath):
        os.makedirs(spath)

    for url in co_urls:
        print(url[0])
        crops = getContent(url[0])
        if crops:
            sfile = url[0].split('/')[-2] + ".json"
            fp = open(spath + sfile, "w", encoding="utf-8")
            json.dump(crops, fp)
            fp.close()


    tEnd = time.time()#計時結束
    end = time.strftime("%m-%d %H:%M:%S")
    print('done!! 花費:', (tEnd - tStart), 'sec')
    print(start, ' ~ ', end)
