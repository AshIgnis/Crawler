#拿到页面源代码 requests
#正则表达式提取想要信息 re

import requests
import re
import csv
import time

s = 0

url = f"https://movie.douban.com/top250?start={s}"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
    'Referer': 'https://movie.douban.com/top250'
}

f = open("data.csv",mode="w",newline='')
csvwriter = csv.writer(f)
csvwriter.writerow(["name", "year", "score", "num"])

for s in range(0, 250, 25):
    resp = requests.get(url, headers=headers)

    page_content = resp.text

    obj = re.compile(r'<li>.*?<div class="item">.*?<span class="title">(?P<name>.*?)'
                    r'</span>.*?<div class="bd">.*?<br>(?P<year>.*?)&nbsp'
                    r'.*?<span class="rating_num" property="v:average">(?P<score>.*?)</span>'
                    r'.*?<span>(?P<num>.*?)人评价',re.S)

    result = obj.finditer(page_content)
    for it in result:
        # print(it.group("name"))
        # print(it.group("year").strip())
        # print(it.group("score"))
        # print(it.group("num").strip())
        dic = it.groupdict()
        dic['year'] = dic['year'].strip()
        csvwriter.writerow(dic.values())
    resp.close() 
    time.sleep(0.5)  # 避免请求过快，添加延时
f.close()
