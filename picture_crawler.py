from bs4 import BeautifulSoup
import requests
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
    'Referer': 'https://pic.netbian.com/4k/index_61.html'
}

url = "https://pic.netbian.com/4k/index_61.html"
domain = "https://pic.netbian.com/"
resp = requests.get(url, headers=headers)
resp.encoding = 'gbk'

main_page = BeautifulSoup(resp.text, 'html.parser')
a_list = main_page.find("div", class_="slist").find("ul",class_="clearfix").find_all("a")
for a in a_list:
    a_href = a.get("href")
    child_url = domain + a_href
    child_resp = requests.get(child_url, headers=headers)
    child_resp.encoding = 'gbk'
    child_resp_text = child_resp.text
    child_page = BeautifulSoup(child_resp_text, 'html.parser')
    img_tag = child_page.find("div", class_="view").find("img").get("src")
    img = domain + img_tag.lstrip("/")

    img_resp = requests.get(img, headers=headers)
    with open(img_tag.split("/")[-1], mode="wb") as f:
            f.write(img_resp.content)
    time.sleep(0.5)
    child_resp.close()

resp.close()