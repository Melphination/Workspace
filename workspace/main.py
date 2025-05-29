import tkinter as tk
from tkinter import ttk
from share import start
from matcher_ui import matcher_ui

try:
    root = tk.Tk()
    root.title("THE PATTERN")
    root.iconbitmap("./images/logo.ico")
    imgtk = tk.PhotoImage(file="./images/logo.png")
    panel = ttk.Label(root, image=imgtk)
    panel.pack()

    mode = tk.StringVar(root)

    def check():
        global mode

        panel.pack_forget()
        mode_label.pack_forget()
        mode_options.pack_forget()
        mode_select.pack_forget()
        mode_button.pack_forget()

        # 0: 매칭 시스템, 1: 공유 플랫폼
        match (mode.get()):
            case "공유 플랫폼":
                start(root)
            case "매칭 시스템":
                matcher_ui(root)
            case _:
                raise Exception(f"Unknown mode {mode.get()}")

    def show():  
        mode_label.config(text=mode.get())  

    # Dropdown options  
    modes = ["매칭 시스템", "공유 플랫폼"]  
    #TODO: Bug fix
    # Selected option variable  
    mode = tk.StringVar(value=modes[0])  

    # Dropdown menu  
    mode_options = ttk.OptionMenu(root, mode, *modes)
    mode_options.pack()  

    # Button to update label  
    mode_select = ttk.Button(root, text="모드 선택", command=show)
    mode_select.pack()  

    mode_label = ttk.Label(root, text=" ")  
    mode_label.pack()  

    mode_button = ttk.Button(root, text="확인", command=check)
    mode_button.pack()

    # 윈도우 사이즈 조절
    root.geometry("500x500")
    root.mainloop()
except BaseException as e:
    root.destory()
    print(e)
