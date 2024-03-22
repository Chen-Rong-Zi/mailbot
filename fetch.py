import re
import os
import sys
import time
import json
import base64
import random
import string
import zipfile
import requests
import toml

'''
    安装此库的方法：
        pip install crypto
        pip install pycryptodome
        然后把 Python 安装目录下 ./Lib/site-packages/crypto 改成首字母大写的 Crypto
'''
from authserver import authserver
from logger     import fetch_log as log


class printer:
    session = None
    id_map = {
        '本科学位证明': '1373833631222497282',
        '本科毕业证明': '1354632827907375105',
        '英文电子成绩单': '1252873888887504897',
        '中文电子成绩单': '1252793153417674754',
        '中英文在学证明': '1202512333918732289',
        '英文自助打印成绩单': '1202512253492953090',
        '中文自助打印成绩单': '1202512157040738305',
        '中文在学（学籍）证明': '1202512079915876353'
    }

    def __init__(self, session:object):
        '''
            传入统一身份认证的 session

            session: 统一身份认证成功后的 session
        '''

        self.session = session
        self.session.headers.update({
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'LoginMode': 'ADMIN',
            'Origin': 'http://zzfwx.nju.edu.cn',
            'Referer': 'http://zzfwx.nju.edu.cn/wec-self-print-app-console/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'appId': '80019'
        })

        # 访问自助打印网站，获取专有 Cookies
        self.session.get('http://zzfwx.nju.edu.cn/wec-self-print-app-console/admin/login/IDS?&returnUrl=/')

    def get_url(self, item_name: str, stu_id: int):
        '''
            获取 stu_id（学号）对应 item_name 类型的材料

            item_name: 材料类型
            stu_id:    学生学号
            stu_name:  学生中文姓名
        '''

        try:
            params = {
                # 选择的证明文件种类，每一种都有固定的
                'itemId': self.id_map[item_name],
                # 代表导出方案为单个导出
                'schemeId': '1166533502928420866',
                # 学号
                'ID': stu_id,
                'pageNumber': '1',
                'pageSize': '10',
            }

            # 验证学号是否正确
            res_1 = self.session.get(
                'http://zzfwx.nju.edu.cn/wec-self-print-app-console/item/sp-batch-export/item/user/page',
                params=params, verify=False
            )

            res_1 = res_1.json()
            # 登录失败则返回的 data 为空
            if not res_1['data']:
                log.logger.error(f'''资料获取失败，错误：{res_1['msg']}，服务器返回：{res_1}''')
                raise Exception(f'''登录失效，服务器报错：{res_1['msg']}''')

            name_list = res_1['data']['records']
            if name_list == []:
                log.logger.error(f'资料获取失败，未查询到学号 {stu_id} 对应的学生 {stu_name}')
                raise Exception('学号错误')

            json_data = {
                'itemId': self.id_map[item_name],
                'itemName': item_name,
                'users': [
                    {
                        'id': name_list[0]['ID'],
                        'name': name_list[0]['NAME'],
                    },
                ],
                'groupUserIds': '',
                'singleUserCount': '50',
                'schemeId': '1166533502928420866',
                'groupBy': ''
            }

            # 获取任务 id
            res_2 = self.session.post(
                'http://zzfwx.nju.edu.cn/wec-self-print-app-console/item/sp-batch-export/task/create',
                json=json_data, verify=False
            )

            # 获取下载 url
            url = 'http://zzfwx.nju.edu.cn/wec-self-print-app-console/item/sp-batch-export/task/{}'\
                .format(res_2.json()['data'])

            for counter in range(0, 10):
                time.sleep(3)
                res_3 = self.session.get(url=url, verify=False)
                res_3 = res_3.json()

                # 出现错误信息
                if res_3['errorLog']:
                    log.logger.error(f'''资料下载失败，服务器返回错误信息：{res_3['errorLog']}''')
                    raise Exception(f'''资料下载失败，服务器返回错误信息：{res_3['errorLog']}''')
                # 下载成功
                if res_3['downloadUrl']:
                    return res_3['downloadUrl']

            # 30s 仍然无法获得下载链接，结束并返回获取失败
            log.logger.error('资料下载失败，获取下载链接轮询超时')
            raise Exception('资料下载失败，获取下载链接超时')
        except requests.Timeout:
            log.logger.error('资料下载失败，请求超时')
            raise Exception('资料下载失败，请求超时，请检查网络连接')

class fetcher:
    uid            = 0
    auth           = None
    printer        = None
    user_data      = {}
    user_data_path = './data/{}.dat'
    user_file_path = './files/{}/'

    # 从表格多选项到下载内容的映射
    download_map = {
        '中英文在学证明': [
            {'name': '中英文在学证明', 'file': '中英文在学证明'}
        ],
        '中文电子成绩单': [
            {'name': '中文电子成绩单', 'file': '中文电子成绩单'}
        ],
        '英文成绩单': [
            {'name': '英文电子成绩单', 'file': '英文电子成绩单'}
        ],
        '本科学位证明': [
            {'name': '本科学位证明', 'file': '本科学位证明'}
        ],
        '本科毕业证明': [
            {'name': '本科毕业证明', 'file': '本科毕业证明'}
        ]
    }

    def __init__(self, uid:int):
        '''
            初始化一个用户数据获取对象

            uid: 用户唯一 id
        '''
        # 设置用户 id
        self.uid       = uid
        self.user_data = self.read_user_data()
        self.username, self.password = self.read_admin_data()
        self.auth = authserver(self.username, self.password)
        self.auth.login()

    def read_user_data(self):
        '''
            根据用户 id 读取用户数据
        '''
        data = os.environ['data'][self.uid]
        return json.load(data)

    def read_admin_data(self):
        '''
            读取管理员数据，
            并实现统一身份认证登录
        '''
        # 获取统一身份认证登陆账户及密码
        # test
        config    = json.loads(os.environ['config'])
        username  = config['nju']['username']
        password  = config['nju']['password']
        return username, password

    def store_file(self, url:str, file_name:str):
        '''
            通过 url 下载文件并存入对应目录，
            并将 zip 文件解压，取出其中的 pdf

            url: 文件下载链接
            file_name: 需要保存的文件名（不带扩展名）
        '''

        try:
            file_path = self.user_file_path.format(self.uid)
            zip_path = f'{file_path+file_name}.zip'
            pdf_path = f'{file_path+file_name}.pdf'

            # 校验需要写入的文件是否已经存在，存在则删除
            if os.path.exists(pdf_path):
                os.remove(pdf_path)

            # 写入内容
            file_data = self.auth.session.get(url).content
            with open(zip_path, 'wb') as file:
                file.write(file_data)

            # 解压缩
            zip_file = zipfile.ZipFile(zip_path, 'r')

            # 判断压缩文件是否为空
            if len(zip_file.namelist()) < 1:
                log.logger.error(f'解压出错，压缩文件位置：{zip_path}')
                Exception('解压出错，压缩文件为空')

            # 解压首个文件
            file = zip_file.namelist()[0]
            zip_file.extract(file, file_path)
            zip_file.close()

            # 修改文件名，并删除压缩包
            os.rename(file_path+file, pdf_path)
            os.remove(zip_path)
        except Exception as err:
            log.logger.error(f'学生 {self.uid} 的资料文件 {file_name} 写入出错，错误：{err}')
            raise Exception(f'文件写入出错，错误：{err}')

    def fetch_data(self):
        try:
            # 初始化爬虫对象
            self.printer = printer(self.auth.session)

            # 验证并新建文件夹
            if not os.path.exists(f'./files/{self.uid}'):
                os.mkdir(f'./files/{self.uid}')

            # 获取资料 url 并下载到本地存储文件夹
            stu_id = self.user_data['user']
            for item in self.user_data['list']:
                for mapping in self.download_map[item]:
                    url = self.printer.get_url(mapping['name'], stu_id)
                    self.store_file(url, mapping['file'])
        except Exception as err:
            log.logger.error(f'学生 {self.uid} 下载出错，错误：{err}')
            raise Exception(f'下载出错，错误：{err}')

def main(uid:str):
    '''
        主函数，根据 uid 获取学生数据
    '''

    # 开始运行程序
    try:
        fetcher_obj = fetcher(uid)
        fetcher_obj.fetch_data()
        exit(0)
    except Exception as err:
        print(f'获取资料出错，错误：{err}', file=sys.stderr)
        exit(1)

if __name__ == '__main__':
    # 从外部接收 uid
    main(sys.argv[1])
