import tkinter      as     tk
import tkinter.ttk  as     ttk
import tkinter.font as     font

from   console      import Console
from   config       import Config
from   statusbar    import StautsBar
from   table        import Table

class Client:
    def __init__(self):
        self.window = tk.Tk()
        self.cmd = Console(self.window)
        self.bar = StautsBar(self.window)

        self.notebook = ttk.Notebook(self.window)
        self.tbl = Table(self.notebook)
        self.cfg = Config(self.notebook)
        self.notebook.add(self.tbl, text='查询列表')
        self.notebook.add(self.cfg, text='配置文件')

    def run(self):
        self.bar.grid(row=0,      column=0, sticky='nsew')
        self.notebook.grid(row=1, column=0, sticky='nsew')
        self.cmd.grid(row=2,      column=0, sticky='nsew')

        self.window.rowconfigure(0, weight=1)
        self.window.rowconfigure(1, weight=10)
        self.window.rowconfigure(2, weight=6)
        self.window.columnconfigure(0, weight=5)
        self.window.mainloop()


if __name__ == '__main__':
    clt = Client()
    clt.window.title("不可缩放的窗口")
    clt.window.geometry("800x700")
    clt.window.resizable(True, True)
    # custom_font = font.Font(size=200)
    # clt.window.option_add("*Font", custom_font)
    clt.window.call("source", "azure.tcl")
    clt.window.call("set_theme", "dark")
    clt.run()

