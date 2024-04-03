import json
import toml
import requests
import hashlib
from   time            import sleep
from   threading       import Thread

from   functional.util import compose, curry
from   global_variable import configuration
from   handler         import Handler

def encrypt(time, user):
    key         = 'Xz4uXT7m4KN33vN59D'
    pwstr       = f'{time}{key}{user}'
    bpwstr      = pwstr.encode('UTF-8')
    passwd_hash = hashlib.md5(bpwstr).hexdigest()
    return passwd_hash

class Poster:
    def __init__(self):
        self.obj = {
            "user"          : "client",
            "time"          : "client",
            "passwd"        : encrypt("client", "client"),
            "configuration" : None,
        }
        ip          = configuration['ip']
        port        = configuration['port']
        self.url    = f'http://{ip}:{port}'
        self.header = { 'Content-Type': 'application/json' }

    def set_config(self, post):
        ip   = post['mailbot']['ip']
        port = post['mailbot']['port']
        ping = Handler.apply(lambda :requests.get(f'http://{ip}:{port}'))
        if isinstance(ping, requests.Response):
            global configuration
            configuration['ip']   = ip
            configuration['port'] = port
            print(f'修改ip、port成功')
        else:
            print(f'修改ip、port失败')

    def post_config(self, config, callback):
        def helper():
            post_data = dict(self.obj)
            post_data['configuration'] = toml.dumps(config)
            res = Handler.apply(lambda :requests.post(self.url, headers=self.header, data=json.dumps(post_data)))
            if isinstance(res, requests.Response):
                print(Poster.pretty_print(res.json()))
            else:
                print(f'发送请求失败')

            self.set_config(config)
            sleep(1)
            callback()

        thread = Thread(target=helper)
        trash  = thread.start()

    def pretty_print(item):
        if not isinstance(item, dict):
            return str(item)
        pretty_dict = json.dumps(item, indent=4, sort_keys=False, ensure_ascii=False)
        return str(pretty_dict)

post = Poster()
