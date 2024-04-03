from threading       import Thread
from time            import sleep

from requests        import post
from global_variable import configuration

import tkinter as tk

class StautsBar(tk.Frame):
    def __init__(self, master):
        super().__init__(master=master)
        self.lbl_status = tk.Label(
                master=self,
                text="",
                foreground='green',
                font=("-size", 10, "-weight", "normal"),
            )
        self.install()
        self.run()

    def install(self):
        self.lbl_status.pack(side=tk.LEFT, padx=30)

    def run(self):
        def update():
            while 1:
                ip = configuration['ip']
                port = configuration['port']
                res = None
                try:
                    res = post(f'http://{ip}:{port}', json={'client' : 'I am client!'})
                except Exception as err:
                    print(f'连接错误， 错误：{err}')
                if res:
                    self.lbl_status.config(
                            text=f"    已连接至{configuration['ip']}:{configuration['port']}",
                            foreground='green'
                    )
                else:
                    self.lbl_status.config(
                            text="󰖪  断开连接",
                            state="normal",
                            foreground='red'
                    )
                sleep(5)

        thread = Thread(target=update)
        thread.start()
