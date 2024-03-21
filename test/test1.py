from seatable_api import Base, context
server_url = context.server_url or 'https://table.nju.edu.cn'
api_token  = context.api_token  or 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJkdGFibGVfdXVpZCI6ImY4MWNhYzIyLWI5ZDQtNGFlNi05OTI5LWMzN2RmMDg4YjQ4MCIsImFwcF9uYW1lIjoiczRsZC5weSIsImV4cCI6MTcwMjcxMjEwOX0.I4XubXF9tu4nwsWaSwhd8x8SqlBtwloRZtIQDO6IVLI'


base = Base(api_token, server_url)
base.auth()
a    = base.get_metadata()
# b = #版次
sqlc = '''UPDATE Table1 set 模板是否发送成功=True where num=%d''' % (b)
print(sqlc)
base.query(sqlc)
