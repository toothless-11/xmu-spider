import requests
from bs4 import BeautifulSoup
import smtplib
import os
from email.mime.text import MIMEText
from email.header import Header

# 目标及配置
URL = "https://cxw.xmu.edu.cn/cms/0qRRjDIv4uaDz4FcwMRk00-1"
MAIL_USER = os.environ.get('MAIL_USER')
MAIL_PASS = os.environ.get('MAIL_PASS')

def send_email(title, link):
    msg = MIMEText(f"新比赛：{title}\n地址：{link}", 'plain', 'utf-8')
    msg['Subject'] = Header("【新比赛提醒】" + title[:15], 'utf-8')
    msg['From'] = MAIL_USER
    msg['To'] = MAIL_USER
    try:
        s = smtplib.SMTP_SSL("smtp.qq.com", 465)
        s.login(MAIL_USER, MAIL_PASS)
        s.sendmail(MAIL_USER, [MAIL_USER], msg.as_string())
        s.quit()
        print("Done: Email sent")
    except Exception as e:
        print(f"Error: {e}")

def main():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(URL, headers=headers, timeout=15)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        item = soup.find('a', title=True)
        if not item: return
        
        title, link = item['title'].strip(), item['href']
        if not link.startswith('http'): link = "https://cxw.xmu.edu.cn" + link

        # 核心逻辑：读取旧记录，对比
        fname = "last_title.txt"
        old_title = open(fname, 'r', encoding='utf-8').read().strip() if os.path.exists(fname) else ""

        if title != old_title:
            print(f"New: {title}")
            send_email(title, link)
            with open(fname, 'w', encoding='utf-8') as f: f.write(title)
        else:
            print("No update")
    except Exception as e:
        print(f"Runtime Error: {e}")

if __name__ == "__main__":
    main()
