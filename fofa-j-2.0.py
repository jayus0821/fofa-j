# !/usr/bin/env python3
# coding: utf-8

import requests,sys,base64
from urllib.parse import quote
from bs4 import BeautifulSoup
import os
import csv,numpy.compat.setup
import time

fofa_url = "https://fofa.so/result"

def banner():
    print('''
  _____       _____                      __ 
_/ ____\_____/ ____\____                |__|
\   __\/  _ \   __\\__  \    ______     |  |
 |  | (  <_> )  |   / __ \_ /_____/     |  |
 |__|  \____/|__|  (____  /         /\__|  |
                        \/          \______|
                                    by jayus
    ''')
   
def get_num_of_result(search):
    global fofa_url
    tmp_url = fofa_url + "?qbase64=" + quote(base64.b64encode(search.encode('utf-8')), 'utf-8')
    #print(tmp_url)
    res = requests.get(url = tmp_url)
    soup = BeautifulSoup(res.text, 'lxml')
    number = soup.select('#rs')[0].span.string.replace(',','')
    print("[+] " + "共找到" + number + "个结果")
    print("[+] " + "需要抓取的数量：")
    get_num = str(input())
    return get_num, number




def get_page_text(get_num,search,auth_cookie,page):
    cookies = "_fofapro_ars_session=" + auth_cookie +  "; result_per_page=" + get_num + "; "
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0","Cookie":"{}search_history=%22%E9%94%90%E6%8D%B7%E7%BD%91%E7%BB%9C-EWEB%E7%BD%91%E7%AE%A1%E7%B3%BB%E7%BB%9F%22; Hm_lvt_9490413c5eebdadf757c2be2c816aedf=1610352315,1610444645,1610452725,1610452804; referer_url=%2Fresult%3Fqbase64%3DIumUkOaNt%252Be9kee7nC1FV0VC572R566h57O757ufIg%253D%253D%26page%3D3; Hm_lpvt_9490413c5eebdadf757c2be2c816aedf=1610457645".format(cookies)}
    #print(header)
    global fofa_url
    tmp_url = fofa_url + "?qbase64=" + quote(base64.b64encode(search.encode('utf-8')), 'utf-8') + "&page=" + str(page)
    #print(tmp_url)
    res = requests.get(url = tmp_url, headers = header)
    #print(res.text)
    print("[+] ","抓取页面完毕，页面长度为" + str(len(res.text)) )
    return res.text

def clean_data(text):
    soap = BeautifulSoup(text, 'lxml')
    dirty_results = soap.select('div[class="right-list-view-item clearfix"]')
    clean_results = []
    for i in range(len(dirty_results)):
        result = []
        target_url = dirty_results[i].select('a[target="_blank"]')[0].get('href')
        #print(target_url)
        target_title = dirty_results[i].select('div[class="time"]')[0].string
        #print(target_title)
        status_code = dirty_results[i].select('div[class="scroll-wrap-res"]')[0].string.split('\r\n')[0].strip()
        #print(status_code)
        result = [target_url, target_title, status_code]
        clean_results.append(result)
    #print(clean_results)
    print("[+] ","数据清洗完毕，抓取数量为" + str(len(clean_results)) )
    return clean_results

def output_to_file(filename, result):
    filename = filename + '.csv'
    if os.path.exists(filename):
        os.remove(filename)
    with open(filename,'w',newline='',encoding='utf-8') as f:
        writer = csv.writer(f)
        try:
            writer.writerow(["url","title","status_code"])
        except Exception as e:
            print(e)
        for rowdict in result:
            #print(rowdict)
            writer.writerow(rowdict)



if __name__ == '__main__':
    banner()
    num_per_time = 2000 #每次抓取多少
    ###fofa限制了只能查一万条，改cookie超过一万条了直接报错了
    ###第一个版本一次抓一万条504
    ###新版本可以分页抓到一万条，默认是每页2000条
    if len(sys.argv) < 4:
        print('''Usage:请输入参数\n例如:python fofa-j.py 'app="Solr"' Solr  94bbbb177c4a564feddb8c7d413d5d61 y\n例如:python fofa-j.py 'app="Solr"'(Fofa搜索语法) Solr(搜索结果文件名)  94bbbb177c4a564feddb8c7d413d5d61(Fofa的Cookie的_fofapro_ars_session值) y(保存页面内容)''')
        exit(0)
    search = sys.argv[1]
    print(search)
    filename = sys.argv[2]
    auth_cookie = sys.argv[3]
    store = sys.argv[4]
    get_number = get_num_of_result(search)[0]
    if int(get_number) > num_per_time:
        page_num = (int(get_number) // num_per_time) + 1
    result = []
    alltext = ''
    for page in range(1,page_num+1):
        print("[+] 抓取第 %d 页..." % (page))
        # if page != page_num:
        text = get_page_text(str(num_per_time),search,auth_cookie,str(page))
        # else:
        #     text = get_page_text(str(int(get_number) - num_per_time*(page - 1)),search,auth_cookie,str(page))
        alltext += text
        for i in clean_data(text):
            result.append(i)
        print(len(result))
        print()
        time.sleep(3)
    
    print("[+] 共抓取到 %d 个结果" % len(result))
    # for i in result:
    #     print(i)

    if store == "y":
        store_name = filename + '.html'
        with open(store_name,'w',encoding='utf-8') as f:
            f.write(alltext)
    output_to_file(filename,result)


# fofa 存在一个cookie参数，为result_per_page，控制每一页现实的目标数量，控制它就可以实现在一页中抓到所有目标...
