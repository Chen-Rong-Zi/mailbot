import re
import random
import string
import base64
import requests
import json

from   Crypto.Cipher import AES
from   util.logger   import fetch_log as log

class authserver:
    def __init__(self, username: str, password: str, ocr_token: str):
        self.session   = requests.Session()
        self.username  = username
        self.password  = password
        self.ocr_token = ocr_token

    def encrypt_password(self, password_seed: str)->str:
        '''
            返回加密后的密码
            From 某学长的 Github: https://github.com/NJU-uFFFD/DDLCheckerCrawlers/blob/main/crawlers/NjuSpocCrawler.py
            逆向 javascript 得到的加密代码，使用 Python 重写

            password_seed: AES 加密算法的参数
        '''
        random_iv  = ''.join(random.sample((string.ascii_letters + string.digits) * 10, 16))
        random_str = ''.join(random.sample((string.ascii_letters + string.digits) * 10, 64))

        data = random_str + self.password
        key  = password_seed.encode("utf-8")
        iv   = random_iv.encode("utf-8")

        bs = AES.block_size

        def pad(s):
            return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)

        cipher = AES.new(key, AES.MODE_CBC, iv)
        data   = cipher.encrypt(pad(data).encode("utf-8"))
        return base64.b64encode(data).decode("utf-8")

    def need_captcha(self):
        '''
            和网站交互，确定验证码
        '''

        need_url = f'https://authserver.nju.edu.cn/authserver/needCaptcha.html'
        res      = self.session.post(need_url, data={'username': self.username})
        return 'true' in res.text

    def get_captch(self, online: bool)->str:
        '''
            获取验证码的结果并返回

            online: 是否调用在线付费 API 识别验证码
        '''

        captch_url = 'https://authserver.nju.edu.cn/authserver/captcha.html'
        captch_img = self.session.get(captch_url).content

        if not online:
            # 本地存档一份当前验证码
            with open('chaptch.jpg', 'wb') as img_output:
                img_output.write(captch_img)
            return input('请输入验证码：')

        captch_img = 'data:image/jpg;base64,{}'.format(base64.b64encode(captch_img).decode('utf-8'))
        data       = {'image': captch_img, 'token': self.ocr_token, 'type': 10110}
        headers    = { 'Content-Type': 'application/json' }
        res        = requests.post('http://api.jfbym.com/api/YmServer/customApi', data=json.dumps(data), headers=headers)

        if res.status_code == 405:
            log.logger.error('OCR 接口拒绝服务：返回值 405，请检查 P 认证')
            raise Exception('OCR 接口拒绝服务')

        res = res.json()
        if res['code'] == 10000:
            return res['data']['data']
        elif res['code'] == 10002:
            log.logger.error(f'OCR 接口欠费，接口返回：{res}')
            raise Exception('OCR 接口欠费，请联系开发人员处理')

        log.logger.error(f'''OCR 接口遇到未知错误，错误码：{res['code']}''')
        raise Exception(f'''OCR 接口遇到未知错误，错误码：{res['code']}''')

    def login(self, online:bool=True):
        '''
            统一身份认证登录，无返回，会建立的一个 session 会话，
            在外部通过 <authserver_object>.session.get/post() 可以顺利访问需要认证的页面

            online: 是否调用在线付费 API 识别验证码，默认调用
        '''

        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'})

        index_url = 'https://authserver.nju.edu.cn/authserver/login?service=http%3A%2F%2Fzzfwx.nju.edu.cn%2Fwec-self-print-app-console%2Fadmin%2Flogin%2FIDS%3FreturnUrl%3D%252F'
        index_page = self.session.get(index_url).content.decode('utf-8')

        password_seed = re.search(r'pwdDefaultEncryptSalt = \"(.*?)\"', index_page).group(1)

        form = {
            'username': self.username,
            'password': self.encrypt_password(password_seed),
            'captchaResponse': self.get_captch(online),
            'lt': re.search(r'name="lt" value="(.*?)"', index_page).group(1),
            'execution': re.search(r'name="execution" value="(.*?)"', index_page).group(1),
            '_eventId': re.search(r'name="_eventId" value="(.*?)"', index_page).group(1),
            'rmShown': re.search(r'name="rmShown" value="(.*?)"', index_page).group(1),
            'dllt': 'userNamePasswordLogin',
        }

        try:
            login_url = 'https://authserver.nju.edu.cn/authserver/login'
            res = self.session.post(url=login_url, data=form, allow_redirects=False)

            if res.status_code == 302:
                return self.session
            else:
                log.logger.error(f'登录失败，请检查用户名和密码是否正确，\
                                服务器返回值：{res.status_code}')
                raise Exception('登录失败，请检查用户名和密码是否正确')
        except requests.Timeout:
            log.logger.error('登录失败，请求超时')
            raise Exception('登录失败，请求超时，请检查网络连接')
