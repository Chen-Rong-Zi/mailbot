import json
import hashlib
import threading
import requests
import tkinter         as     tk
from   tkinter         import messagebox
import tkinter.ttk     as     ttk
from   ttkwidgets      import CheckboxTreeview
from   seatable_api    import Base

from   functional.util import curry, compose
from   global_variable import get_url
from   poster          import encrypt

server_url = 'https://table.nju.edu.cn'
api_token  = '56128d59ebfaf66936a14228cd92351ef100fd36'

key_values = {
    'stu_id'            : '学号',
    'en_name'           : '英文姓名',
    'zh_name'           : '中文姓名',
    'mail'              : '邮箱地址',
    'company_mail'      : '单位邮箱地址',
    'material'          : '申请材料',
    'application_time'  : '申请时间',
    'mail_send_time'    : '邮件发送时间',
    'phone'             : '联系电话',
    'is_material_ready' : '材料是否下载',
    'is_mail_ready'     : '邮件是否生成',
    'is_sent'           : '邮件是否发送'
}


class ButtonFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(master=parent)
        self.parent = parent
        self.btn_send = ttk.Button(
                self,
                text='发送邮件',
                style='Accent.TButton',
                command=self.send_mail()
            )
        self.btn_query = ttk.Button(
                self,
                text='更新',
                style='Accent.TButton',
                command=self.parent.query()
            )
        self.btn_delete = ttk.Button(
                self,
                text='删除',
                style='Accent.TButton',
                command=lambda  :self.parent.delete_all()
            )
        self.btn_preview = ttk.Button(
                self,
                text='获取生成邮件',
                style='Accent.TButton',
                command=self.get_preview()
            )
        self.install()
    def install(self):
        self.btn_send.grid(row=0, column=0)
        self.btn_query.grid(row=0, column=1)
        self.btn_delete.grid(row=0, column=2)
        self.btn_preview.grid(row=0, column=3)
        self.rowconfigure(0, weight=1)
        self.columnconfigure([0, 1, 2, 3], weight=3)

    def get_preview(self):
        def get_data(stu_id):
            return {
                'stu_id' : stu_id,
                'application_time' : 0,
                'passwd' : encrypt(0, stu_id),
                'preview' : 'client'
            }
        def inner():
            self.btn_preview.state(['disabled'])
            self.btn_preview.config(text="下载中, 请稍候")
            self.update()
            working_list = [
                    curry(map, 2)(self.parent.ctv.item),
                    curry(map, 2)(lambda item : item['values'][0]),
                    curry(map, 2)(lambda data : requests.post(url=get_url(), json=get_data(data))),
                    curry(map, 2)(lambda content : content.json()),
                    curry(filter, 2)(lambda  item : 'email' in item or print(item)),
                    curry(map, 2)(lambda  item : item['email']),
                    curry(list, 1),
                ]
            emails = compose(working_list, self.parent.ctv.get_checked())
            working_list = [
                    curry(map, 2)(self.parent.ctv.item),
                    curry(map, 2)(lambda item : item['values'][0]),
                    curry(list, 1),
                ]
            stu_ids = compose(working_list, self.parent.ctv.get_checked())

            for id, email in zip(stu_ids, emails):
                filepath = f'email/{id}.eml'
                with open(filepath, 'w') as f:
                    f.write(email)
                print(f'已经保存{filepath}')
            self.btn_preview.state(['!disabled'])
            self.btn_preview.config(text="获取生成邮件")
        def thread():
            td = threading.Thread(target=inner)
            td.start()
        return thread

    def send_mail(self):
        def make_data(*args):
            return {
                "stu_id": args[0],
                "en_name": args[1],
                "zh_name": args[2],
                "mail": args[3],
                "company_mail": args[4],
                'send': True,
                "application_time": args[5],
                "passwd": encrypt(args[5], args[0]),
            }

        def inner():
            node = self.parent.ctv.get_checked()
            if len(node) > 1 or len(node) <= 0:
                return messagebox.showinfo('Info', '请每一次只发送一个请求')
            base = Base(api_token, server_url)
            base.auth()
            item = self.parent.ctv.item(node[0])
            result = base.query(f"""select 学号, 英文姓名, 中文姓名, 邮箱地址, 单位邮箱地址, 申请时间 from Table1 where 学号 = {item["values"][0]} order by 申请时间 Desc limit 1""")
            print(requests.post(url=get_url(), json=make_data(*result[0].values())).content.decode('unicode_escape'))
        return inner


class Table(tk.Frame):
    def __init__(self, master):
        super().__init__(master=master)
        self.nodes = []
        self.ctv = CheckboxTreeview(
                self,
                columns=tuple(key_values.keys()),
                show='tree headings'
            )
        self.bar = ttk.Scrollbar(self,
                orient=tk.VERTICAL,
                command=self.ctv.yview
            )
        self.ctv.configure(yscroll=self.bar.set)
        self.frm_btn = ButtonFrame(self)

        self.ctv.column('#0', width=6)
        for k, v in key_values.items():
            self.ctv.heading(k, text=v)
            self.ctv.column(k, width=5, anchor='center')
        self.make_category()
        self.install()

    def make_category(self):
        self.append(tuple('' for i in range(12)), text='已发送', iid=0, open=True)
        self.append(tuple('' for i in range(12)), text='待发送', iid=1)
        self.append(tuple('' for i in range(12)), text='其他',   iid=2)

    def delete_all(self):
        self.ctv.delete(*self.ctv.get_children(''))

    def append(self, value, **kw):
        assert isinstance(value, tuple) and len(value) == 12, f'插入数据格式不正确, 错误: {value}'
        node = self.ctv.insert('', tk.END, values=value, **kw)
        self.nodes.append(node)
        return node

    def append_by_status(self, value, **kw):
        node = self.append(value=value, **kw)
        if value[-1] == 'True':
            self.ctv.move(node, 0, 0)
        elif value[-2] == 'True':
            self.ctv.move(node, 1, 0)
        else:
            self.ctv.move(node, 2, 0)

    def install(self):
        self.ctv.grid(row=1, column=0, sticky='nsew')
        self.bar.grid(row=1, column=1, sticky='nsew')
        self.frm_btn.grid(row=0, column=0, sticky='nsew')
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=10)
        self.columnconfigure(0, weight=5)

    def query(self):
        def inner():
            base = Base(api_token, server_url)
            base.auth()
            self.delete_all()
            self.make_category()
            working_list = [
                     lambda base : base.query('select * from Table1 order by 学号 desc '),
                     curry(map, 2)(lambda  item : tuple(item.values())),
                     curry(map, 2)(lambda  x : tuple(str(i) for i in x)),
                     curry(map, 2)(lambda item : item[1:13]),
                     curry(map, 2)(self.append_by_status),
                     lambda  x : list(x),
                     ]
            compose(working_list, base)
        return inner

