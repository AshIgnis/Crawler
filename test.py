
import requests
url = 'https://www.baidu.com/s?wd=IP'
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36 Edg/86.0.622.56'
}
reponse = requests.get(url,headers,proxies={"https":'182.16.171.1:53281'})
page_text = reponse.text
with open ('ip.html','w',encoding='utf-8') as s :
    s.write(page_text)

