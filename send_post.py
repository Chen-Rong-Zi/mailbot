from seatable_api import Base, context
import requests
import json
import hashlib
import time
server_url = context.server_url or 'https://table.nju.edu.cn'
api_token  = context.api_token  or '3d26582817a4ee8abcf640024b309451f9eaa3c4'


base = Base(api_token, server_url)
base.auth()
a    = base.query('select * from Table1 order by 名称 desc limit 0,1')[0]
print(a)
hl   = hashlib.md5()
ts   = time.time()
user = base.query('select 学号 from Table1 order by 名称 desc limit 0,1')[0]['学号']
key  = 'Xz4uXT7m4KN33vN59D'
str  = str(ts)+key+str(user)
print(str)
hl.update(str.encode(encoding = 'utf-8'))
print('MD5加密后为 ：' + hl.hexdigest())
passwd = hl.hexdigest()
user_data = {
    'passwd':passwd,
    'time':ts,
    'id':   base.query('select 名称           from Table1 order by 名称 desc limit 0,1')[0]['名称'],
    'user': base.query('select 学号           from Table1 order by 名称 desc limit 0,1')[0]['学号'],
    'name': base.query('select 申请人英文姓名 from Table1 order by 名称 desc limit 0,1')[0]['申请人英文姓名'],
    'dist': base.query('select 申请单位邮箱   from Table1 order by 名称 desc limit 0,1')[0]['申请单位邮箱'],
    'self': base.query('select 申请人邮箱     from Table1 order by 名称 desc limit 0,1')[0]['申请人邮箱'],
    'list': base.query('select 附加材料列表   from Table1 order by 名称 desc limit 0,1')[0]['附加材料列表']
}
print(user_data)

url = "http://114.212.99.252:8080"
data = user_data
print(data)
res = requests.post(url = url,data = json.dumps(data))

