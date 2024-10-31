"""
This file is part of file_size.
Copyright (C) 2024  xkk1

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import platform
import tkinter as tk
from tkinter import ttk
import tkinter.filedialog
import tkinter.messagebox
import tkinter.scrolledtext

import file_size


def show_information(information="", title="文件大小"):
    """显示信息"""
    global information_window
    global information_scrolledtext
    
    def save_txt(information=information, title=title):
        filename = tkinter.filedialog.asksaveasfilename(
            title='请选择你要保存的地方',
            filetypes=[('TXT', '*.txt'), ('所有文件', '*')],
            initialfile='%s' % title,
            defaultextension = '.txt',  # 默认文件的扩展名
        )  # 返回文件名--另存为
        if type(filename) != str or filename == '':
            return False
        else:
            try:
                with open(filename, 'w', encoding="UTF-8") as f:
                    f.write(information)
                tkinter.messagebox.showinfo("保存文件", f"保存文件 {filename} 成功！")
                return True
            except Exception as e:
                tkinter.messagebox.showerror("保存文件错误", "保存文件时发生错误！\n" + str(e))
                return False

    try:
        information_window.deiconify()
        information_window.title(title)
        information_scrolledtext.delete(0.0, tk.END)
        information_scrolledtext.insert(tk.END, information)

    except:
        information_window = tk.Tk()
        if platform.system() == 'Windows': 
            try:
                import ctypes
                #告诉操作系统使用程序自身的dpi适配
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
                #获取屏幕的缩放因子
                ScaleFactor=ctypes.windll.shcore.GetScaleFactorForDevice(0)
                #设置程序缩放
                information_window.tk.call('tk', 'scaling', ScaleFactor/75)
            except:
                pass
        information_window.title(title)
        information_scrolledtext = tkinter.scrolledtext.ScrolledText(
            information_window,
            width=96,
            height=32,
            undo=True
        )  # 滚动文本框
        information_scrolledtext.pack(expand=tk.YES, fill=tk.BOTH, padx=5, pady=5)
 
        information_scrolledtext.insert(tk.INSERT, information)

        
        '''创建一个弹出菜单'''
        menu = tk.Menu(information_window,
            tearoff=False,
        )

        menu.add_command(label="剪切", command=lambda:information_scrolledtext.event_generate('<<Cut>>'))
        menu.add_command(label="复制", command=lambda:information_scrolledtext.event_generate('<<Copy>>'))
        menu.add_command(label="粘贴", command=lambda:information_scrolledtext.event_generate('<<Paste>>'))
        menu.add_command(label="删除", command=lambda:information_scrolledtext.event_generate('<<Clear>>'))
        menu.add_command(label="撤销", command=lambda:information_scrolledtext.event_generate('<<Undo>>'))
        menu.add_command(label="重做", command=lambda:information_scrolledtext.event_generate('<<Redo>>'))
        def popup(event):
            menu.post(event.x_root, event.y_root)  # post在指定的位置显示弹出菜单

        information_scrolledtext.bind("<Button-3>", popup)  # 绑定鼠标右键,执行popup函数
        
        bottom_frame = tk.Frame(information_window)
        bottom_frame.pack()
        
        save_button = ttk.Button(
                bottom_frame,
                text="保存为文本文档(*.txt)",
                command=lambda:save_txt(information=information_scrolledtext.get('1.0', tk.END).rstrip()))
        save_button.pack(side=tk.RIGHT, padx=5,pady=5)

        close_button = ttk.Button(
                bottom_frame,
                text="关闭",
                command=information_window.destroy)
        close_button.pack(side=tk.RIGHT, padx=5,pady=5)

        def copy_to_clipboard():
            """Copy current contents of text_entry to clipboard."""
            information_window.clipboard_clear()  # Optional.
            information_window.clipboard_append(information_scrolledtext.get('1.0', tk.END).rstrip())
        
        copy_button = ttk.Button(
                bottom_frame,
                text="复制内容到剪贴板",
                command=copy_to_clipboard,
                )
        copy_button.pack(side=tk.LEFT, padx=5,pady=5)
        
        information_window.mainloop()

def main():
    show_information(file_size.get_show_information())


if __name__ == "__main__":
    main()
