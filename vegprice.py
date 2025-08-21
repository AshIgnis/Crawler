import requests
import csv

url = "http://www.xinfadi.com.cn/getPriceData.html"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
    'Referer': 'http://www.xinfadi.com.cn/priceDetail.html'
}

resp = requests.post(url, headers=headers)
data = resp.json()
f = open("vegprice.csv", mode="w", newline='', encoding='utf-8')
csvwriter = csv.writer(f)
csvwriter.writerow(data.values())
resp.close()