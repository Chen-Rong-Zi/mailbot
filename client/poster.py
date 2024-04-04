import json
import toml
import requests
import hashlib
from   time            import sleep
from   threading       import Thread

from   functional.util import compose, curry
from   global_variable import configuration
from   handler         import Handler

#  material
def encrypt(time, user):
    key         = 'Xz4uXT7m4KN33vN59D'
    pwstr       = f'{time}{key}{user}'
    bpwstr      = pwstr.encode('UTF-8')
    passwd_hash = hashlib.md5(bpwstr).hexdigest()
    return passwd_hash

class Poster:
    def __init__(self):
        self.obj = {
            "stu_id"           : "client",
            "application_time" : "client",
            "passwd"           : encrypt("client", "client"),
            "configuration"    : None,
        }
        ip          = configuration['ip']
        port        = configuration['port']
        self.url    = f'http://{ip}:{port}'
        self.header = { 'Content-Type': 'application/json' }

    def set_config(self, post):
        ip   = post['mailbot']['ip']
        port = post['mailbot']['port']
        ping = Handler.apply(lambda :requests.post(f'http://{ip}:{port}', json=self.obj))
        if isinstance(ping, requests.Response):
            global configuration
            configuration['ip']   = ip
            configuration['port'] = port
            print(f'修改ip、port成功')
        else:
            print(f'修改ip、port失败')

    def post_config(self, config, callback):
        def helper():
            self.set_config(config)
            post_data = dict(self.obj)
            post_data['configuration'] = toml.dumps(config)
            res = Handler.apply(lambda :requests.post(self.url, headers=self.header, json=post_data))
            if isinstance(res, requests.Response):
                print(Poster.pretty_print(res.json()))
            else:
                print(f'发送请求失败')

            sleep(1)
            callback()

        thread = Thread(target=helper)
        trash  = thread.start()

    def pretty_print(item):
        if not isinstance(item, dict):
            return str(item)
        pretty_dict = json.dumps(item, indent=4, sort_keys=False, ensure_ascii=False)
        return str(pretty_dict)

    def ping(ip, port):
        res = None
        try:
            res = requests.post(f'http://{ip}:{port}', json={'stu_id' : 'client', 'application_time' : 'client', 'passwd' : encrypt('client', 'client')})
        except Exception as err:
            print(f'连接错误， 错误：{err}')
        return True if res else False

post = Poster()
