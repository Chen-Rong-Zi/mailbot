import json
import toml
import hashlib

import seatable_api
from   seatable_api        import Base, context
from   requests.exceptions import MissingSchema

from   util.logger         import mailbot_log as log

def encrypt(time, user):
    key         = 'Xz4uXT7m4KN33vN59D'
    pwstr       = str(time) + key + str(user)
    bpwstr      = pwstr.encode('UTF-8')
    passwd_hash = hashlib.md5(bpwstr).hexdigest()
    return passwd_hash

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
            api_token = config['table']['api_token']
            server    = config['table']['server']
            # for test
            server_url = 'https://table.nju.edu.cn'
            api_token  = '3d26582817a4ee8abcf640024b309451f9eaa3c4'
            base      = Base(api_token,  server_url)
            base.auth()
            return base
        except AssertionError:
            log.logger.error('admin.toml出错')
            return False
        except MissingSchema:
            log.logger.error('token或server参数不合法')
            return False
        except KeyError:
            log.logger.error('config错误')
            return False
        except ConnectionError:
            log.logger.error('Base连接失败，请求被拒绝')
            return False
        except Exception:
            log.logger.error('Base验证失败')
            return False

    def valid_stuid(stu_id, itemId, session):
        try:
            params = {
                # 选择的证明文件种类，每一种都有固定的
                'itemId': itemId,
                # 代表导出方案为单个导出
                'schemeId': '1166533502928420866',
                # 学号
                'ID': stu_id,
                'pageNumber': '1',
                'pageSize': '10',
            }

            # 验证学号是否正确
            result = session.get('http://zzfwx.nju.edu.cn/wec-self-print-app-console/item/sp-batch-export/item/user/page', params=params, verify=False).json()
            if result['data'] is None:
                raise Exception(f'''登录失效，服务器报错：{result['msg']}''')

            if result['data']['records'] == []:
                log.logger.error(f'资料获取失败，未查询到学号 {stu_id} 对应的学生 {stu_name}')
                raise Exception('学号错误')

            return result['data']['records']
        except Exception as err:
            log.logger.error(err)
            return False

    def valid_post(content):
        try:
            post        = json.loads(content)
            user        = post['user']
            time        = post['time']
            passwd      = post['passwd']
            passwd_hash = encrypt(time, user)
            if 'id' in post:
                id      = post['id']
                name    = post['name']
                dist    = post['dist']
                self    = post['self']
                list    = post['list']
            elif 'word' in post:
                word    = post['word']
                version = post['version']
            elif 'account' in post:
                version = post['version']
                key     = post['key']
            elif passwd_hash != post['passwd']:
                raise AssertionError
            return post
        except json.decoder.JSONDecodeError:
            log.logger.error('用户输入非json字符串')
            return False
        except KeyError:
            log.logger.error('用户请求json不完整')
            return False
        except AssertionError:
            log.logger.error('用户请求密码错误')
            return False
        except Exception:
            log.logger.error('post请求无效')
            return False
