import json
import requests

text = '''{"user": 231880291, "name": "Baijun Chen", "dist": "2014078563@qq.com","self": "231880291@smail.nju.edu.cn","list": ["本科学位证明", "中英文在学证明", "本科毕业证明"]}'''
obj = json.loads(text)
# s = json.dumps(obj)
# print(s)
# print(type(obj), type(json.loads(s)))

url = 'http://114.212.99.252:8080'
header = {
    'Content-Type': 'application/json'
}
res = requests.post(url, headers = header, data = json.dumps(obj))

print(res.status_code, res.text)