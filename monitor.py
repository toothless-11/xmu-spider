import requests
import smtplib
import os
from email.mime.text import MIMEText
from email.header import Header
from bs4 import BeautifulSoup

# 爬取目标
URL = "https://cxw.xmu.edu.cn/cms/0qRRjDIv4uaDz4FcwMRk00-1"
FILENAME = "last_title.txt"
MAIL_USER = os.environ.get('MAIL_USER') 
MAIL_PASS = os.environ.get('MAIL_PASS') 

def send_email(title, link):
    msg_content = f"<h3>发现新比赛：{title}</h3><p><a href='{link}'>点击此处查看详情</a></p>"
    message = MIMEText(msg_content, 'html', 'utf-8')
    message['From'] = Header("比赛监控", 'utf-8')
    message['To'] = Header("提醒自己", 'utf-8')
    message['Subject'] = Header("【新比赛提醒】" + title[:15], 'utf-8')
    try:
        smtp_obj = smtplib.SMTP_SSL("smtp.qq.com", 465)
        smtp_obj.login(MAIL_USER, MAIL_PASS)
        smtp_obj.sendmail(MAIL_USER, [MAIL_USER], message.as_string())
        print("邮件已发送")
    except Exception as e:
        print(f"邮件发送失败: {e}")

def run():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(URL, headers=headers, timeout=15)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        item = soup.find('a', title=True)
        if not item: return

        curr_title = item['title'].strip()
        curr_link = item['href']
        if not curr_link.startswith('http'):
            curr_link = "https://cxw.xmu.edu.cn" + curr_link

        old_title = ""
        if os.path.exists(FILENAME):
            with open(FILENAME, 'r', encoding='utf-8') as f:
                old_title = f.read().strip()

        if curr_title != old_title:
            send_email(curr_title, curr_link)
            with open(FILENAME, 'w', encoding='utf-8') as f:
                f.write(curr_title)
        else:
            print("网页还没更新")
    except Exception as e:
        print(f"执行出错: {e}")

if __name__ == "__main__":
    run()