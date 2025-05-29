from tkinter import ttk
import tkinter as tk
from tksheet import Sheet
from itertools import zip_longest
from secure import safety_check, email_format_check, send_email
from argon2 import PasswordHasher
from nava import play
from connect_db import users

ph = PasswordHasher()

# TODO: share.py를 여러 파일로 나누기

root = None
alpha = "ABCD"


# 로그인 후 룸메이트와 패턴을 공유할 수 있는 윈도우
def share(username):
    global root
    user = users.find_one({"username": username})
    me_sheet = Sheet(
        root,
        data=[[username], *[[" ".join(pattern)] for pattern in user["patterns"]]],
        height=520,
        width=200,
    )
    me_sheet.enable_bindings("all")
    me_sheet.pack()
    roommates = user["roommate"]
    # 룸메이트의 패턴을 모두 묶음
    roommate_patterns = zip_longest(
        *[
            list(map(lambda x: " ".join(x), users.find_one({"username": roommate})["patterns"]))
            for roommate in roommates
        ],
        fillvalue="",
    )
    roommate_patterns = list(roommate_patterns)
    roommate_sheet = Sheet(
        root,
        data=[roommates, *roommate_patterns],
        height=520,
        width=200 * len(roommates),
    )
    roommate_sheet.pack()


def verify_code(email, username, pw, code_var, code, widgets):
    for widget in widgets:
        widget.destroy()
    if code_var != code:
        wrong_label = ttk.Label(root, text="인증 코드가 틀렸습니다.")
        wrong_label.pack()
    else:
        add_user(email, username, pw, widgets)
    start(root)


def verify_info(email, username, pw, widgets):
    play("./sounds/button.mp3")
    message = "이메일 또는 아이디가 중복되어 있습니다."
    if not safety_check(pw.get()):
        message = "비밀번호가 규칙에 맞지 않습니다."
    else:
        gra = email_format_check(email.get())
        if gra == -1:
            message = "이메일 형식이 맞지 않거나 재학생이 아닙니다."
        else:
            code = send_email(email.get())
            for widget in widgets:
                widget.destroy()
            code_var = tk.StringVar(root)
            code_label = ttk.Label(root, text="인증 코드를 입력해주세요.")
            code_label.pack()
            code_entry = ttk.Entry(root, textvariable=code_var)
            code_entry.pack()
            code_button = ttk.Button(
                root,
                text="인증",
                command=lambda: verify_code(
                    email,
                    username,
                    pw,
                    code_var.get(),
                    code,
                    [code_label, code_entry, code_button, *widgets],
                ),
            )
            code_button.pack()
            return
    for widget in widgets:
        widget.pack()
    wrong_label = ttk.Label(root, text=message)
    wrong_label.pack()


def add_user(email, username, pw):
    email_not_found = not (users.find_one({"email": email.get()}))
    username_not_found = not (users.find_one({"username": username.get()}))
    if username_not_found and email_not_found:
        users.insert_one(
            {
                "username": username.get(),
                "email": email.get(),
                "pw": ph.hash(pw.get()),
                "patterns": [],
                "roommate": [],
                "summary": {
                    "wake_up": "07:00:00",
                    "sleep": "01:00:00",
                    "early_bird": 0,
                    "light_off": [0, 0],
                    "air": "12:40:00",
                    "study": ["00:00:00-01:00:00", "23:00:00-00:00:00"]
                },
                "gender": "M",
                "grade": 1,
                "room": 500,
            }
        )
        return
    raise Exception("Invalid username or email")


def verify(username, pw, widgets):
    play("./sounds/button.mp3")
    # 비밀번호가 알맞는지 체크
    # 아이디가 틀려도 False가 나옴
    found = users.find_one({"username": username.get()})
    if found and ph.verify(found["pw"], pw.get()):
        for widget in widgets:
            widget.destroy()
        share(username.get())
    else:
        # 비밀번호나 아이디가 틀렸음을 알림
        wrong_label = ttk.Label(root, text="비밀번호나 아이디가 틀렸습니다.")
        wrong_label.pack()


# 로그인을 할 수 있는 윈도우
def login(widgets):
    for widget in widgets:
        widget.destroy()
    username = tk.StringVar(root)
    pw = tk.StringVar(root)
    root.title("패턴 공유 플랫폼 - 로그인")
    username_label = ttk.Label(root, text="아이디")
    username_label.pack()
    username_entry = ttk.Entry(root, textvariable=username)
    username_entry.pack()
    pw_label = ttk.Label(root, text="비밀번호")
    pw_label.pack()
    pw_entry = ttk.Entry(root, textvariable=pw)
    pw_entry.pack()
    login_button = ttk.Button(
        root,
        text="로그인",
        command=lambda: verify(
            username,
            pw,
            [username_label, username_entry, pw_label, pw_entry, login_button],
        ),
    )
    login_button.pack()


def signup(widgets):
    for widget in widgets:
        widget.pack_forget()
    email = tk.StringVar(root)
    username = tk.StringVar(root)
    pw = tk.StringVar(root)
    root.title("패턴 공유 플랫폼 - 회원가입")
    email_label = ttk.Label(root, text="이메일")
    email_label.pack()
    email_entry = ttk.Entry(root, textvariable=email)
    email_entry.pack()
    username_label = ttk.Label(root, text="아이디")
    username_label.pack()
    username_entry = ttk.Entry(root, textvariable=username)
    username_entry.pack()
    pw_label = ttk.Label(root, text="비밀번호")
    pw_label.pack()
    pw_entry = ttk.Entry(root, textvariable=pw)
    pw_entry.pack()
    login_button = ttk.Button(
        root,
        text="회원가입",
        command=lambda: verify_info(
            email,
            username,
            pw,
            [
                email_label,
                email_entry,
                username_label,
                username_entry,
                pw_label,
                pw_entry,
                login_button,
            ],
        ),
    )
    login_button.pack()


# 로그인 또는 회원가입을 선택할 수 있는 윈도우
def start(rt):
    global root
    root = rt
    login_button = ttk.Button(
        root, text="로그인", command=lambda: login([login_button, signup_button])
    )
    login_button.pack()
    signup_button = ttk.Button(
        root, text="회원가입", command=lambda: signup([login_button, signup_button])
    )
    signup_button.pack()
