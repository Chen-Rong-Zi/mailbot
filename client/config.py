import tkinter     as tk
import tkinter.ttk as ttk

from poster          import post
from functional.util import compose, curry
from global_variable import configuration


config_format = {
    "统一身份认证区": [
        "username",
        "password"
    ],

    "邮件区": [
        "email",
        "token"
    ],

    "表格api":[
        "server",
        "api_token"
    ],

    "邮件机器人":[
        "ip",
        "port"
    ],

    "ocr token":[
        "token"
    ]
}

def find_childrens(filter_func, frame):
    def helper(frame):
        if not isinstance(frame, tk.Frame):
            return [frame]
        return sum([helper(widget) for widget in frame.winfo_children()], [])
    return list(filter(filter_func, helper(frame)))

def make_config(args):
    return {
        "nju" : {
            "username" : args[0],
            "password" : args[1]
        },
        "email" : {
            "emai" : args[2],
            "token" : args[3]
        },
        "table" : {
            "server" : args[4],
            "api_token" : args[5]
        },
        "mailbot" : {
            "ip" : args[6],
            "port" : args[7]
        },
        "ocr" : {
            "token" : args[8]
        }
    }

def make_title_Label(master, title):
    return ttk.Label(
        master,
        text='[' + title+ ']',
        width=10,
        justify="right",
        font=("-size", 12, "-weight", "bold"),
    )

def make_key_Label(master, key):
    return  ttk.Label(
        master,
        text=key,
        foreground='#abb2bf',
        justify="center",
        font=("-size", 11, "-weight", "normal"),
    )

def make_Entry(master):
    return ttk.Entry(
            master,
            font=("-size", 9, "-weight", "normal"),
            width=30
        )

def make_item_Frame(master, title, keys):
    frm_item  = tk.Frame(master=master)
    lbl_title = make_title_Label(frm_item, title)
    lbl_keys  = [make_key_Label(frm_item, key) for key in keys]
    ent_vals  = [make_Entry(frm_item) for i in range(len(keys))]

    lbl_title.grid(row=0, sticky='nsew', padx=10)
    for row, (lbl_key, ent_val) in enumerate(zip(lbl_keys, ent_vals)):
        lbl_key.grid(row=row + 1, column=0, sticky='nsew', padx=20)
        ent_val.grid(row=row + 1, column=1, sticky='nsew')

    frm_item.rowconfigure(list(range(len(ent_vals))), weight=1)
    frm_item.columnconfigure([0, 1], weight=1)
    return frm_item


class Config(tk.Frame):
    def __init__(self, frame):
        self.parent_frame = frame
        super().__init__(master=self.parent_frame)
        self.frm_items = [make_item_Frame(self, *item) for item in config_format.items()]
        self.btn_update = tk.Button(
                master=self,
                text="更新配置文件",
                font=("-size", 9, "-weight", "normal"),
                command=self.update_config()
            )
        self.install()

    def install(self):
        for frm in self.frm_items:
            frm.pack(fill=tk.BOTH, expand=True)
        self.btn_update.pack(fill=tk.BOTH)


    def update_config(self):
        def response():
            self.btn_update.config(
                    text="更新配置文件",
                    state="normal"
                )

        def update():
            self.btn_update.config(
                    text="等待服务器相应",
                    state="disabled"
                )

            config = compose([
                    curry(find_childrens)(lambda x : isinstance(x, ttk.Entry)),
                    curry(map, 2)(lambda ent : ent.get()),
                    curry(list),
                    curry(make_config)
                    ], self)
            post.post_config(config, response)
        return update
