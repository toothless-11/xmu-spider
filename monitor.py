import requests
from bs4 import BeautifulSoup
import smtplib
import os
from email.mime.text import MIMEText
from email.header import Header
import sys

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

        # ========== 修改点1：改用ID集合 ==========
        fname = "notified_ids.txt"
        notified_ids = set()

        if os.path.exists(fname):
            with open(fname, 'r', encoding='utf-8') as f:
                for line in f:
                    notified_ids.add(line.strip())

        # 提取比赛唯一ID（从链接中取最后一段）
        current_id = link.split('/')[-1]
        
        if current_id not in notified_ids:
            print(f">>> 发现新比赛！(ID: {current_id})", flush=True)
            send_email(title, link)
            
            # 更新记录
            notified_ids.add(current_id)
            with open(fname, 'w', encoding='utf-8') as f:
                for id in notified_ids:
                    f.write(id + '\n')
            print(">>> 状态已更新", flush=True)
        else:
            print(f">>> 比赛 {current_id} 已通知过，跳过", flush=True)

    except Exception as e:
        print(f">>> 运行出错: {e}", flush=True)

if __name__ == "__main__":
    main()
