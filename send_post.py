from seatable_api import Base, context
import requests
import json
import hashlib
import time
server_url = context.server_url or 'https://table.nju.edu.cn'
api_token  = context.api_token  or '3d26582817a4ee8abcf640024b309451f9eaa3c4'

def encrypt():
    hl     = hashlib.md5()
    ts     = time.time()
    count  = base.query('select 学号 from Table1 order by 申请时间 desc limit 0,1')[0]['学号']
    key    = 'Xz4uXT7m4KN33vN59D'
    seed   = f'{ts}{key}{count}'
    hl.update(seed.encode(encoding='utf-8'))
    passwd = hl.hexdigest()
    return passwd, ts

base = Base(api_token, server_url)
base.auth()
passwd, ts = encrypt()

user_data = {
    'passwd'           : passwd,
    'application_time' : ts,
    'zh_name'          : base.query('select 中文姓名     from Table1 order by 申请时间 desc limit 0,1')[0]['名称'],
    'stu_id'           : base.query('select 学号         from Table1 order by 申请时间 desc limit 0,1')[0]['学号'],
    'en_name'          : base.query('select 英文姓名     from Table1 order by 申请时间 desc limit 0,1')[0]['英文姓名'],
    'company_mail'     : base.query('select 单位邮箱地址 from Table1 order by 申请时间 desc limit 0,1')[0]['单位邮箱地址'],
    'mail'             : base.query('select 邮箱地址     from Table1 order by 申请时间 desc limit 0,1')[0]['邮箱地址'],
    'material'         : base.query('select 申请材料     from Table1 order by 申请时间 desc limit 0,1')[0]['申请材料']
}

url = "http://114.212.99.252:8080"
data = user_data
print(data)
res = requests.post(url=url,data=json.dumps(data))
print(res)

