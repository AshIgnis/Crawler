import re

#findall: 返回所有匹配的字符串列表
# list = re.findall(r"\d+","我的电话号是10086,我的手机是13800138000")
# print(list)

#finditer: 返回一个迭代器，每个元素是一个匹配对象
# it = re.finditer(r"\d+","我的电话号是10086,我的手机是13800138000")
# for i in it:
#     print(i.group())
    
# search: 返回第一个匹配的对象
# s = re.search(r"\d+","我的电话号是10086,我的手机是13800138000")
# print(s.group())

# # 预加载正则表达式
# itm = re.compile(r"\d+")
# list = itm.findall("我的电话号是10086,我的手机是13800138000")
# print(list)

s = """
<div class='jay'><span id='1'>周杰伦</span></div>
<div class='jj'><span id='2'>林俊杰</span></div>
"""

#(?P<变量名>正则表达式)

obj = re.compile(r"<div class='.*?'><span id='\d+'>(?P<xcy>.*?)</span></div>",re.S) #re.S 使得 . 可以匹配换行符

result = obj.finditer(s)
for i in result:
    print(i.group("xcy"))