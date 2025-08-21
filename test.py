import requests
import json

# url = 'https://www.baidu.com/s?wd=周杰伦'

# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0'
# }

# resp = requests.get(url, headers=headers)
# print(resp.text)

# url = 'https://fanyi.baidu.com/sug'

# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0'
# }

# s = input(" ")

# dat = {
#     'kw': s
# }

# resp = requests.post(url, data = dat, headers = headers)

# print(resp.json())

# url = 'https://m.douban.com/rexxar/api/v2/subject/recent_hot/movie'

# params = {
#     'limit': '50',
# }

# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
#     'Referer':'https://m.douban.com/',
#     'Accept-Language':'zh-CN,zh;q=0.9'
# }

# resp = requests.get(url, params=params, headers=headers)

# data = resp.json()  # 若响应是 JSON
# print(json.dumps(data, ensure_ascii=False, indent=2))

