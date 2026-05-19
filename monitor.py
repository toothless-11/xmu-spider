import requests
from bs4 import BeautifulSoup
import os
import sys

def main():
    print(">>> 步骤1：脚本已启动", flush=True)
    
    url = "https://cxw.xmu.edu.cn/cms/0qRRjDIv4uaDz4FcwMRk00-1"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        print(f">>> 步骤2：尝试连接厦大官网...", flush=True)
        # 设置 10 秒超时，如果 10 秒连不上就报错
        res = requests.get(url, headers=headers, timeout=10)
        print(f">>> 步骤3：收到响应！状态码: {res.status_code}", flush=True)
        
        if res.status_code == 200:
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            news_item = soup.find('li', class_='news')
            
            if news_item:
                title = news_item.find('span', class_='topic').get_text(strip=True).replace('>', '', 1)
                print(f">>> 步骤4：解析成功，标题是: {title}", flush=True)
                
                # 保存文件
                with open("last_title.txt", "w", encoding="utf-8") as f:
                    f.write(title)
                print(">>> 步骤5：已写入 last_title.txt", flush=True)
            else:
                print(">>> 步骤4失败：没找到 class='news' 的标签", flush=True)
        else:
            print(f">>> 步骤3失败：网页返回了错误代码 {res.status_code}", flush=True)
            
    except requests.exceptions.Timeout:
        print(">>> 错误：连接超时！GitHub 访问不了厦大官网，可能是被学校防火墙拦截了。", flush=True)
    except Exception as e:
        print(f">>> 发生其他错误: {e}", flush=True)

if __name__ == "__main__":
    main()
