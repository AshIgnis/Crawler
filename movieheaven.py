import requests
import re

domain = "https://www.dytt8899.com/"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'
}

resp = requests.get(domain, headers=headers)
resp.encoding = 'gbk'  # 设置编码为 gbk

obj1 = re.compile(r'2025必看热片.*?<ul>(?P<ul>.*?)</ul>',re.S)
obj2 = re.compile(r"<a href='(?P<urls>.*?)'",re.S)
obj3 = re.compile(r'<div class="title_all"><h1>.*?《(?P<title>.*?)》.*?<td style="WORD-WRAP: break-word" bgcolor="#fdfddf"><a href="(?P<magnet>.*?)"', re.S)

results = obj1.finditer(resp.text)
child_href_list = []

for it in results:
    ul = it.group("ul")
    
    rsls = obj2.finditer(ul)
    for url in rsls:
        child_href = domain + url.group('urls').strip("/")
        child_href_list.append(child_href)

resp.close()

for child_url in child_href_list:
    child_resp = requests.get(child_url, headers=headers)
    child_resp.encoding = 'gbk'
    result3 = obj3.search(child_resp.text)
    print(result3.group("title"))
    print(result3.group("magnet"))
    child_resp.close()