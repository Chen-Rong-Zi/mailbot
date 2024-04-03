import json
import requests
from   util.validate import encrypt

obj = {
    "stu_id"           : 231220088,
    "en_name"          : "Rongzi Chen",
    "company_mail"     : "231220088@smail.nju.edu.cn",
    "zh_name"          : "陈翔宇",
    "application_time" : 1,
    "passwd"           : encrypt(1, 231220088),
    # 'preview'          : True,
    "mail"             : "19708876912@163.com",
    # "material": ["本科学位证明", "中英文在学证明", "本科毕业证明"]
    # "material": ['英文电子成绩单', '中文电子成绩单', '英文自助打印成绩单', '中文自助打印成绩单', '中文在学（学籍）证明']
    "material": ['中英文在学证明', '中文电子成绩单', '英文电子成绩单', '本科学位证明', '本科毕业证明', '英文自助打印成绩单', '中文自助打印成绩单', '中文在学（学籍）证明']
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
