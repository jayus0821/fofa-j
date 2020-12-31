# !/usr/bin/env python3
# coding: utf-8

import requests,sys,base64
from urllib.parse import quote
from bs4 import BeautifulSoup
import os
import csv,numpy.compat.setup

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





#get_num_of_result('"WFManager"')

def get_page_text(get_num,search,auth_cookie):
    cookies = {
        "_fofapro_ars_ession" : auth_cookie, "result_per_page" : get_num
    }
    #print(cookies)
    global fofa_url
    tmp_url = fofa_url + "?qbase64=" + quote(base64.b64encode(search.encode('utf-8')), 'utf-8')
    res = requests.get(url = tmp_url, cookies = cookies)
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
    with open(filename,'w',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["url","title","status_code"])
        for rowdict in result:
            print(rowdict)
            writer.writerow(rowdict)



if __name__ == '__main__':
    banner()
    if len(sys.argv) < 4:
        print('''Usage:请输入参数\n例如:python fofa-j.py 'app="Solr"' Solr  94bbbb177c4a564feddb8c7d413d5d61 y\n例如:python fofa-j.py 'app="Solr"'(Fofa搜索语法) Solr(搜索结果文件名)  94bbbb177c4a564feddb8c7d413d5d61(Fofa的Cookie的_fofapro_ars_session值) y(保存页面内容)''')
        exit(0)
    search = sys.argv[1]
    filename = sys.argv[2]
    auth_cookie = sys.argv[3]
    store = sys.argv[4]
    get_number = get_num_of_result(search)[0]
    text = get_page_text(get_number,search,auth_cookie)
    if store == "y":
        store_name = filename + '.html'
        with open(store_name,'w',encoding='utf-8') as f:
            f.write(text)
    result = clean_data(text)
    output_to_file(filename,result)


# fofa 存在一个cookie参数，为result_per_page，控制每一页现实的目标数量，控制它就可以实现在一页中抓到所有目标...
