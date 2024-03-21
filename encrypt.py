from seatable_api import Base, context
import hashlib
import time

hl    = hashlib.md5()
ts    = time.time()
count = base.query('select 学号 from Table1 order by 名称 desc limit 0,1')[0]['学号']
key   = 'Xz4uXT7m4KN33vN59D'
str   = str(ts) + key + str(count)
print(str)
hl.update(str.encode(encoding = 'utf-8'))
print('MD5加密后为 ：' + hl.hexdigest())
passwd    = hl.hexdigest()
user_data = {
    'passwd' : passwd,
    'time'   : ts,
    'id'     : base.query('select 名称           from Table1 order by 名称 desc limit 0,1')[0]['名称'],
    'user'   : base.query('select 学号           from Table1 order by 名称 desc limit 0,1')[0]['学号'],
    'name'   : base.query('select 申请人英文姓名 from Table1 order by 名称 desc limit 0,1')[0]['申请人英文姓名'],
    'dist'   : base.query('select 申请单位邮箱   from Table1 order by 名称 desc limit 0,1')[0]['申请单位邮箱'],
    'self'   : base.query('select 申请人邮箱     from Table1 order by 名称 desc limit 0,1')[0]['申请人邮箱'],
    'list'   : base.query('select 附加材料列表   from Table1 order by 名称 desc limit 0,1')[0]['附加材料列表']
}
print(user_data)

# post1:(管理员账号)
ts = time.time()
key = 'Xz4uXT7m4KN33vN59D'
str = str(ts) + key
print(str)
hl.update(str.encode(encoding = 'utf-8'))
print('MD5加密后为 ：' + hl.hexdigest())
passwd = hl.hexdigest()
user_data = {
  'passwd':passwd,
  'time':ts,
  'version': base.query('select 版次 from Table1 order by time desc limit 0,10')[0]['版次'],
  'account': base.query('select 统一身份认证账号 from Table1 order by time desc limit 0,10')[0]['统一身份认证账号'],
  'key': base.query('select 统一身份认证密码 from Table1 order by time desc limit 0,10')[0]['统一身份认证密码']}
print(user_data)

# post2:（邮件模板）
hl = hashlib.md5()
ts = time.time()
key = 'Xz4uXT7m4KN33vN59D'
str = str(ts) + key
print(str)
hl.update(str.encode(encoding = 'utf-8'))
print('MD5加密后为 ：' + hl.hexdigest())
passwd = hl.hexdigest()
p = base.query('select 邮件模板 from Table1 order by time desc limit 0,10')[0]['邮件模板']
print(p)
user_data = {
  'passwd':passwd,
  'time':ts,
  'version': base.query('select 版次 from Table1 order by time desc limit 0,10')[0]['版次'],
  'word':base.query('select 邮件模板 from Table1 order by time desc limit 0,10')[0]['邮件模板']
    }

