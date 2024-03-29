import json
import toml
import hashlib
from cryptography.fernet import Fernet

import seatable_api
from   seatable_api        import Base, context
from   requests.exceptions import MissingSchema

from   util.error          import UpdateConfigError, BaseTokenError
from   util.logger         import mailbot_log
from   util.logger         import fetch_log

def encrypt(time, user):
    key         = 'Xz4uXT7m4KN33vN59D'
    pwstr       = str(time) + key + str(user)
    bpwstr      = pwstr.encode('UTF-8')
    passwd_hash = hashlib.md5(bpwstr).hexdigest()
    return passwd_hash

class Validator:
    def valid_config(config_str=None):
        try:
            if config_str is None:
                with open("admin.toml", 'r', encoding='utf-8') as file:
                    config = toml.load(file)
            else:
                config = toml.loads(config_str)
            nju       = config['nju']
            username  = nju['username']
            password  = nju['password']
            email     = config['email']
            token     = email['token']
            table     = config['table']
            api_token = table['api_token']
            server    = table['server']
            if not Validator.valid_base(config):
                raise BaseTokenError('base验证未通过')
            return config
        except toml.decoder.TomlDecodeError as err:
            mailbot_log.logger.error(f'admin.toml格式不正确, 错误: {err}')
            return False
        except FileNotFoundError:
            mailbot_log.logger.error('未找到admin.toml')
            return False
        except KeyError:
            mailbot_log.logger.error('admin.toml缺少相应键值对')
            return False
        except Exception as err:
            mailbot_log.logger.error(f'admin.toml出错, 错误: {err}')
            return False

    def valid_base(config):
        try:
            api_token = config['table']['api_token']
            server    = config['table']['server']
            # test
            # mailbot_log.logger.error(f"{api_token = }, {server = }")
            base      = Base(api_token,  server)
            base.auth()
            return base
        except AssertionError:
            mailbot_log.logger.error('admin.toml出错')
            return False
        except MissingSchema:
            mailbot_log.logger.error('token或server参数不合法')
            return False
        except KeyError:
            mailbot_log.logger.error('config错误')
            return False
        except ConnectionError as err:
            mailbot_log.logger.error(f'Base连接失败，请求被拒绝, 错误:{err}')
            return False
        except Exception as err:
            mailbot_log.logger.error(f'Base验证失败, 未知错误：{str(err)}' )
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
                fetch_log.logger.error(f'登陆失效')
                raise Exception(f'''登录失效，服务器报错：{result['msg']}''')

            if result['data']['records'] == []:
                fetch_log.logger.error(f'资料获取失败，未查询到学号 {stu_id} 对应的学生 {stu_name}')
                raise Exception('学号错误')

            return result['data']['records']
        except Exception as err:
            fetch_log.logger.error(err)
            return False

    def valid_post(content):
        try:
            post        = json.loads(content)
            user        = post['user']       # 学号
            time        = post['time']       # 请求时间
            passwd      = post['passwd']     # 验证码
            passwd_hash = encrypt(time, user)
            if 'id' in post:
                id      = post['id']         # 姓名
                name    = post['name']       # 英文姓名
                dist    = post['dist']       # 申请单位邮箱
                self    = post['self']       # 申请人邮箱
                list    = post['list']       # 申请列表
            elif 'word' in post:
                word    = post['word']
                version = post['version']
            elif 'configuration' in post:
                # 配置文件格式检测位于update_config中
                pass

            if passwd_hash != post['passwd']:
                raise AssertionError('密码验证错误')
            return post
        except json.decoder.JSONDecodeError:
            mailbot_log.logger.error('用户输入非json字符串')
            return False
        except KeyError as err:
            mailbot_log.logger.error(f'用户请求json不完整：{err}')
            return False
        except AssertionError:
            mailbot_log.logger.error('用户请求密码错误')
            return False
        except Exception as err:
            mailbot_log.logger.error(f'post请求无效, 错误：{err}')
            return False
