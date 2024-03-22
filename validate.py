import json
import toml
import hashlib

import seatable_api
from   seatable_api        import Base, context
from   requests.exceptions import MissingSchema

from   logger              import mailbot_log as log

class Validator:
    def valid_config():
        try:
            with open("admin.toml", 'r', encoding='utf-8') as file:
                config = toml.load(file)
            nju       = config['nju']
            username  = nju['username']
            password  = nju['password']
            email     = config['email']
            token     = email['token']
            table     = config['table']
            api_token = table['api_token']
            server    = table['server']
            return config
        except toml.decoder.TomlDecodeError:
            log.logger.error('admin.toml格式不正确')
            return False
        except FileNotFoundError:
            log.logger.error('未找到admin.toml')
            return False
        except KeyError:
            log.logger.error('admin.toml缺少相应键值对')
            return False
        except Exception:
            log.logger.error('admin.toml出错')
            return False

    def valid_base():
        try:
            is_config_valid = Validator.valid_config()
            if not is_config_valid:
                raise AssertionError
            config    = is_config_valid
            api_token = config['token']
            server    = config['server']
            base      = Base(api_token,  server)
            base.auth()
            return base
        except AssertionError:
            log.logger.error('admin.toml出错')
            return False
        except MissingSchema:
            log.logger.error('token或server参数不合法')
            return False
        except ConnectionError:
            log.logger.error('Base连接失败，请求被拒绝')
            return False
        except Exception:
            log.logger.error('Base验证失败')
            return False

    def valid_post(content):
        try:
            post        = json.loads(content)
            time        = post['time']
            passwd      = post['passwd']
            user        = post['user']
            key         = 'Xz4uXT7m4KN33vN59D'
            pwstr       = str(time) + key + str(user)
            bpwstr      = pwstr.encode('UTF-8')
            passwd_hash = hashlib.md5(bpwstr).hexdigest()

            if 'word' in post:
                word    = post['word']
                version = post['version']
            elif 'account' in post:
                version = post['version']
                key     = post['key']
            elif passwd_hash != post['passwd']:
                raise AssertionError
            else:
                raise AssertionError

            return post
        except json.decoder.JSONDecodeError:
            log.logger.error('用户输入非json字符串')
            return False
        except KeyError:
            log.logger.error('用户请求不完整')
            return False
        except AssertionError:
            log.logger.error('用户请求非法')
            return False
        except Exception:
            log.logger.error('post请求无效')
            return False

    def valid_stuid():
