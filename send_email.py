import re
import os
import sys
import time
import json
import mammoth

import smtplib
import email
from   email.mime.multipart   import MIMEMultipart
from   email.mime.text        import MIMEText
from   email.mime.application import MIMEApplication
from   email.header           import Header

from   util.logger            import send_email_log as log
# 解析docx文件需安装mammoth库


file_mapping = {
    "本科学位证明": "Certificate of the Bachelor's Degree",
    "本科毕业证明": "Nanjing University Diploma",
    "中文电子成绩单": "Nanjing University Transcript of Academic Records in Chinses",
    "英文电子成绩单": "Nanjing University Transcript of Academic Records in English",
    "中英文在学证明": "Nanjing University Undergraduate Student Certificate",
    "英文自助打印成绩单" : "Self-service printing of transcripts in English",
    "中文自助打印成绩单" : "Self-service printing of transcripts in Chinese",
    "中文在学（学籍）证明" : "Proof of Chinese language study (student status)",
}

class send_email:
    def __init__(self, id: str):
        self.stu_id = id
        self.config = json.loads(os.environ['config'])
        self.data          = json.loads(os.environ['data'])
        self.sender_mail   = self.config['email']['email']
        self.token         = self.config['email']['token']
        self.stu_id        = self.data['stu_id']
        self.en_name       = self.data['en_name']
        self.company_mail  = self.data['company_mail']
        self.mail          = self.data['mail']
        self.material      = self.data['material']
        self.date          = time.strftime("%m/%d/%Y", time.localtime())
        self.body          = None

        title = f"""Official Documents for Transfer Admission—{self.en_name}"""
        self.message = MIMEMultipart()
        self.message["Subject"] = Header(title, "UTF-8")
        self.receiver = [f"""{self.mail}""", f"""{self.company_mail}"""]
        self.message.add_header('From', self.sender_mail)
        self.message.add_header('To', ', '.join(self.receiver))

    def connect_template(self):
        try:
            with open("prototype.docx", "rb") as file:
                result = mammoth.convert_to_html(file)
                self.body = result.value
            log.logger.info("邮件模板连接成功")
        except Exception as err:
            log.logger.error(f"无法读取邮件模板, {err}")
            raise Exception(f"无法读取邮件模板, {err}")

    def attach(self, mark: str):
        self.body = self.body.replace("$$list$$", "<ol> </ol>")
        try:
            try:
                text = f"""<li>A soft copy of {file_mapping.get(mark)}</li>\n"""
                self.body = self.body.replace("</ol>", text + "</ol>")
                att = MIMEApplication(
                    open(f"""./files/{self.stu_id}/{mark}.pdf""", "rb").read()
                )
                att["Content-Type"] = "application/octet-stream"
                att[
                    "Content-Disposition"
                ] = f'''attachment; filename="{file_mapping.get(mark)}.pdf"'''
                self.message.attach(att)
            except:
                log.logger.error(f"""文件错误：不存在{mark}文件""")
                raise Exception(f"""文件错误：不存在{mark}文件""")
        except:
            log.logger.error(f"""不合法的邮件附件参数: {mark}""")
            raise Exception(f"""不合法的邮件附件参数: {mark}""")

        self.body = self.body.replace("$$name$$", self.en_name)
        self.body = self.body.replace("$$date$$", self.date)

    def make_email(self):
        try:
            self.connect_template()
            for item in self.material:
                self.attach(item)
            self.message.attach(MIMEText(self.body, "html", "utf-8"))
            log.logger.info("邮件构建成功")
        except Exception as err:
            log.logger.error("无法构建邮件")
            log.logger.error(err, file=sys.stderr)
            raise Exception("无法构建邮件")

    def save(self):
        self.make_email()
        filepath = f'emails/{self.stu_id}.eml'
        with open(filepath, 'w') as f:
            f.write(self.message.as_string())
        log.logger.info('成功保存邮件')

    def send(self):
        filepath = f'emails/{self.stu_id}.eml'
        with open(filepath) as f:
            self.message = email.message_from_file(f)
        try:
            # 使用学生邮箱测试时，请将host名改为"smtp.exmail.qq.com"
            # host = "smtp.nju.edu.cn"
            # host = "smtp.exmail.qq.com"
            host = "smtp.163.com"
            smtp = smtplib.SMTP_SSL(host, 465)
            smtp.login(self.sender_mail, self.token)
            log.logger.info("邮件服务器连接成功")
        except smtplib.SMTPAuthenticationError:
            log.logger.error("邮箱认证失败，邮箱名或授权码错误")
            raise Exception("邮箱认证失败，邮箱名或授权码错误")

        try:
            smtp.sendmail(self.sender_mail, self.receiver, self.message.as_string())
            log.logger.info("邮件发送成功")
            log.logger.error(f"{self.mail = }, {self.sender_mail = }")
            smtp.quit()
        except Exception as err:
            log.logger.error(f"发送失败, {err}")
            raise Exception(f"发送失败, {err}")

if __name__ == "__main__":
    try:
        a = send_email(sys.argv[1])
        if sys.argv[2] == 'send':
            a.send()
        else:
            a.save()
        sys.exit(0)
    except Exception as err:
        log.logger.error(f"错误：{err}")
        sys.exit(1)
