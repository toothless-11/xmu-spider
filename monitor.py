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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        res = requests.get(URL, headers=headers, timeout=15)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 1. 定位到列表容器
        # 找到第一个 class 为 news 的 li 标签
        news_item = soup.find('li', class_='news')
        if not news_item:
            print("未发现比赛列表，请检查网页结构")
            return

        # 2. 提取链接
        a_tag = news_item.find('a')
        link = a_tag['href']
        if not link.startswith('http'):
            link = "https://cxw.xmu.edu.cn" + link

        # 3. 提取标题
        # 标题在 class="topic" 的 span 标签里
        topic_span = news_item.find('span', class_='topic')
        # get_text() 会拿到包括子标签在内的所有文字，strip() 去掉空格
        # 因为开头有 ">" 符号，我们用 replace 或切片去掉它
        title = topic_span.get_text(strip=True).replace('>', '', 1)

        print(f"当前抓取到：{title}")

        # 4. 核心逻辑：读取旧记录，对比
        fname = "last_title.txt"
        old_title = ""
        if os.path.exists(fname):
            with open(fname, 'r', encoding='utf-8') as f:
                old_title = f.read().strip()

        if title != old_title:
            print(f"检测到更新: {title}")
            send_email(title, link)
            with open(fname, 'w', encoding='utf-8') as f:
                f.write(title)
        else:
            print("没有新比赛")

    except Exception as e:
        print(f"运行出错: {e}")
