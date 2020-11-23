import re
import time
import requests
import pandas as pd
from retrying import retry
from concurrent.futures import ThreadPoolExecutor


start = time.clock  # 计时开始
# plist 为1-100页的URL的编号num
plist = []
for i in range(1, 101):
    j = 44 * (i - 1)
    plist.append(j)
listno = plist
datatmsp = pd.DataFrame(columns=[])
while True:
    @retry(stop_max_attempt_number=8)  # 设置最大重试次数
    def network_programming(num):
        url = 'https://www.iqiyi.com/' + str(num)
        web = requests.get(url, headers=headers)
        web.encoding = 'utf-8'
        return web


    # 多线程
    def multithreading():
        number = listno
        # 每次爬取成功的页
        event = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            for result in executor.map(network_programming, number, chunksize=10):
                event.append(result)
        return event
# 隐藏：修改headers参数
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0'}
listpg = []
event = multithreading()
for i in event:
    json = re.findall('"auctions":(.*?),"recommendAuctions"', i.text)
    if len(json):
        table = pd.read_json(json[0])
        datatmsp = pd.concat([datatmsp, table], axis=0, ignore_index=True)
        pg = re.findall('"pageNum":(.*?),"p4pbottom_up"', i.text)[0]
        listpg.append(pg)  # 记入没一次爬取成功的页码
