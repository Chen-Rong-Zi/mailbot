import sys
import datetime
import tkinter as tk

from seatable_api import Base

class StdoutRedirector:
    def __init__(self, widget, log_file='log/client.log'):
        self.widget = widget
        self.called_time = 0
        self.prefix = lambda : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.logfile = open(log_file, 'a+')

    def write(self, text):
        if text == ' ' or text == '\n': return
        log = f'[{self.prefix()}]\n{text}\n'
        self.widget.configure(state='normal')
        self.widget.insert(tk.END, log)
        self.logfile.write(log)
        self.widget.see(tk.END)
        self.widget.configure(state='disabled')

    def read(self, file):
        pass

    def flush(self):
        self.logfile.close()


class Console(tk.Frame):
    def __init__(self, frame):
        self.parent_frame = frame
        super().__init__(master=self.parent_frame)

        self.txt = tk.Text(
                master=self,
                height=10,
                wrap="word",
                background='#1e2127',
                foreground='#abb2bf',
                state='disabled',
                font=("-size", 12, "-weight", "normal"),
            )
        self.btn_update = tk.Button(
                master=self,
                text="清屏",
                font=("-size", 11, "-weight", "normal"),
                command=self.update_output()
            )
        self.install()
        sys.stdout = StdoutRedirector(self.txt)

    def install(self):
        self.txt.pack(fill="both", expand=True)
        self.btn_update.pack(fill="both", expand=True)

    def update_output(self):
        def inner():
            self.txt.configure(state='normal')
            self.txt.delete("1.0", tk.END)
            self.txt.configure(state='disabled')
            print('清屏')
        return inner
