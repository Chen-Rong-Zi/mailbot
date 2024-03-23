import json
import requests
from   util.validate import encrypt

obj = {
    "user": 231880291,
    "name": "Baijun Chen",
    "dist": "2014078563@qq.com",
    "time": 1,
    "passwd": encrypt(1, 231880291),
    "self": "231880291@smail.nju.edu.cn",
    # "list": ["本科学位证明", "中英文在学证明", "本科毕业证明"]
    "list": ['本科学位证明', '本科毕业证明', '英文电子成绩单', '中文电子成绩单', '中英文在学证明', '英文自助打印成绩单', '中文自助打印成绩单', '中文在学（学籍）证明']
}
text = json.dumps(obj)
# s = json.dumps(obj)
# print(s)
# print(type(obj), type(json.loads(s)))

url = 'http://localhost:8080'
header = {
    'Content-Type': 'application/json'
}
res = requests.post(url, headers = header, data = json.dumps(obj))

print(res.status_code, res.text)
