from datetime import datetime
import secrets, os, re, smtplib, string
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()
charset = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_")

# 안전한 비밀번호인지 판단하는 함수
def safety_check(pw: str):
    return (
        len(pw) >= 8
        and sum(int(c.isupper()) for c in pw) >= 2
        and sum(int(c.islower()) for c in pw) >= 2
        and sum(int(c.isdigit()) for c in pw) >= 2
    )

def valid_id(id: str):
    return len(set(id) - charset) == 0

# 재학생이 맞는지 이메일 형식이 맞는지 확인
# 형식이 맞으면 학년 리턴, 틀리면 -1 리턴
# 휴학생을 위해 신입생보다 4년 일찍 입학한 사람도 포함함
def email_format_check(email: str):
    last = datetime.now().year % 100
    # 3월 1일부터는 신입생 들어옴 가정
    if datetime.today().strftime("%m-%d") < "03-01":
        last -= 1
    if re.fullmatch(
        f"({last - 3}|{last - 2}|{last - 1}|{last})" + r"\d{3}@sshs.hs.kr", email
    ):
        return last - int(email[:2]) + 1
    return -1


N = 8
possible_chars = string.ascii_letters + string.digits

# 이메일 인증을 위한 코드 생성
def gen_code():
    return "".join(secrets.choice(possible_chars) for _ in range(N))


# 이메일 인증
subject = "THE PATTERN 인증 코드"
sender = os.environ["NAVER_MAIL"]
password = os.environ["NAVER_PW"]


def send_email(receipt):
    code = gen_code()
    msg = MIMEText(code)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receipt
    with smtplib.SMTP_SSL("smtp.naver.com", 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, receipt, msg.as_string())
    return code
