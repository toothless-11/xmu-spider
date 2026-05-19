import requests
from bs4 import BeautifulSoup
import smtplib
import os
from email.mime.text import MIMEText
from email.header import Header
import sys

# 从 GitHub Secrets 获取配置
MAIL_USER = os.environ.get('MAIL_USER')
MAIL_PASS = os.environ.get('MAIL_PASS')
URL = "https://cxw.xmu.edu.cn/cms/0qRRjDIv4uaDz4FcwMRk00-1"

def send_email(title, link):
    print(f">>> 正在尝试发送邮件给 {MAIL_USER}...", flush=True)
    if not MAIL_USER or not MAIL_PASS:
        print("错误：未配置 MAIL_USER 或 MAIL_PASS 变量", flush=True)
        return

    msg = MIMEText(f"发现新比赛：{title}\n\n详情链接：{link}", 'plain', 'utf-8')
    msg['Subject'] = Header("【科创提醒】" + title[:20], 'utf-8')
    msg['From'] = MAIL_USER
    msg['To'] = MAIL_USER

    try:
        # QQ邮箱必须使用 SSL，端口 465
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)
        server.login(MAIL_USER, MAIL_PASS)
        server.sendmail(MAIL_USER, [MAIL_USER], msg.as_string())
        server.quit()
        print(">>> 邮件发送成功！", flush=True)
    except Exception as e:
        print(f">>> 邮件发送失败: {e}", flush=True)

def main():
    print(">>> 脚本启动", flush=True)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        res = requests.get(URL, headers=headers, timeout=15)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 定位逻辑（已验证成功）
        news_item = soup.find('li', class_='news')
        if not news_item:
            print("未找到比赛列表", flush=True)
            return

        topic_span = news_item.find('span', class_='topic')
        a_tag = news_item.find('a')
        
        title = topic_span.get_text(strip=True).replace('>', '', 1)
        link = a_tag['href']
        if not link.startswith('http'):
            link = "https://cxw.xmu.edu.cn" + link

        print(f">>> 抓取到最新标题: {title}", flush=True)

        # 读取旧记录对比
        fname = "last_title.txt"
        old_title = ""
        if os.path.exists(fname):
            with open(fname, 'r', encoding='utf-8') as f:
                old_title = f.read().strip()

        if title != old_title:
            print(f">>> 检测到新内容！(旧: {old_title})", flush=True)
            # 1. 发送邮件
            send_email(title, link)
            # 2. 更新本地文件
            with open(fname, 'w', encoding='utf-8') as f:
                f.write(title)
            print(">>> 状态已更新", flush=True)
        else:
            print(">>> 内容无变化，不发送邮件。", flush=True)

    except Exception as e:
        print(f">>> 运行出错: {e}", flush=True)

if __name__ == "__main__":
    main()
