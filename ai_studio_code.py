import os
import re
import json
import time
import base64
import requests
from bs4 import BeautifulSoup, NavigableString, Comment
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from openai import OpenAI

# ================= 配置区 =================
CONFIG_FILE = "menu.json"           
BASE_URL = "https://docs.example.com" 
LOGIN_URL = f"{BASE_URL}/login"
CONTENT_SELECTOR = "main.content-body" 
OUTPUT_DIR = "scraped_docs"

# OpenAI 及其代理配置
API_KEY = "your-api-key"
CUSTOM_BASE_URL = "https://your-proxy-domain.com/v1"
MODEL_NAME = "gpt-4o-mini" 

# 图片过滤配置
SKIP_IMAGE_PREFIX = "xxx" # 以此开头的图片 URL 将被视为头像并跳过

client = OpenAI(api_key=API_KEY, base_url=CUSTOM_BASE_URL)

class DocScraper:
    def __init__(self):
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        
        options = Options()
        self.driver = webdriver.Chrome(options=options)
        self.session = requests.Session()

    def sync_cookies(self):
        """同步 Selenium 登录态到 Session"""
        for cookie in self.driver.get_cookies():
            self.session.cookies.set(cookie['name'], cookie['value'])

    def get_image_base64(self, img_url):
        """下载图片并转 Base64"""
        try:
            resp = self.session.get(img_url, timeout=10)
            if resp.status_code == 200:
                ext = img_url.split('.')[-1].split('?')[0].lower()
                mime = f"image/{ext}" if ext in ['png','jpg','jpeg','gif','webp'] else "image/jpeg"
                b64 = base64.b64encode(resp.content).decode('utf-8')
                return f"data:{mime};base64,{b64}"
        except Exception as e:
            print(f"  [!] 图片下载失败: {img_url} -> {e}")
        return None

    def analyze_img_with_ai(self, img_url):
        """解析图片，包含空校验和前缀过滤"""
        # 1. 空校验
        if not img_url or not str(img_url).strip():
            return None

        # 2. 头像/特定前缀过滤逻辑
        if img_url.startswith(SKIP_IMAGE_PREFIX):
            print(f"  [-] 跳过头像/装饰图: {img_url[:30]}...")
            return None

        # 3. 获取文件流
        b64_data = self.get_image_base64(img_url)
        if not b64_data: return "[无法读取图片内容]"
        
        try:
            res = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": [
                    {"type": "text", "text": "描述图片内容并提取文字。"},
                    {"type": "image_url", "image_url": {"url": b64_data}}
                ]}]
            )
            return res.choices[0].message.content.strip()
        except Exception as e:
            return f"[AI解析报错: {e}]"

    def html_to_md(self, element):
        """递归 HTML 到 Markdown 映射"""
        if isinstance(element, Comment): return ""
        if isinstance(element, NavigableString): return element.string or ""

        tag = element.name
        inner_md = "".join(self.html_to_md(c) for c in element.children)

        match tag:
            case 'h1' | 'h2' | 'h3': return f"\n\n{'#' * int(tag[1])} {inner_md}\n"
            case 'p': return f"\n\n{inner_md}\n"
            case 'strong' | 'b': return f" **{inner_md}** "
            case 'em' | 'i': return f" *{inner_md}* "
            case 'a': return f" [{inner_md}]({element.get('href', '#')}) "
            case 'ul' | 'ol': return f"\n{inner_md}\n"
            case 'li':
                prefix = "1. " if element.parent.name == 'ol' else "* "
                return f"{prefix}{inner_md}\n"
            case 'pre': return f"\n```\n{element.get_text().strip()}\n```\n"
            case 'img':
                src = element.get('src', '').strip()
                # 调用 AI 解析（内部已包含 SKIP_IMAGE_PREFIX 过滤）
                desc = self.analyze_img_with_ai(src)
                
                # 如果返回 None 或者是被跳过的图片，则不生成任何内容
                if desc is None:
                    return ""
                return f"\n\n![img]({src})\n> **AI 图片解析**: {desc}\n\n"
            case 'table': return self._parse_table(element)
            case 'hr': return "\n---\n"
            case _: return inner_md

    def _parse_table(self, table):
        rows = []
        all_tr = table.find_all('tr')
        if not all_tr: return ""
        for tr in all_tr:
            cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
            rows.append(f"| {' | '.join(cells)} |")
        if len(rows) > 0:
            col_count = len(all_tr[0].find_all(['td', 'th']))
            sep = f"| {' | '.join(['---'] * col_count)} |"
            rows.insert(1, sep)
        return "\n" + "\n".join(rows) + "\n"

    def traverse_json(self, nodes, current_path=[]):
        """递归遍历 JSON 菜单树"""
        for node in nodes:
            label = re.sub(r'[\\/:*?"<>|]', '-', node.get('label', 'unnamed'))
            new_path = current_path + [label]
            children = node.get('children', [])
            if children:
                self.traverse_json(children, new_path)
            else:
                target_url = f"{BASE_URL}/{node['belongToSysId']}/{node['id']}"
                self.scrape_page(target_url, new_path)

    def scrape_page(self, url, path_list):
        file_name = "-".join(path_list) + ".md"
        print(f">>> 正在同步: {file_name}")
        try:
            self.driver.get(url)
            time.sleep(2)
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            content = soup.select_one(CONTENT_SELECTOR)
            if content:
                md_body = self.html_to_md(content)
                with open(os.path.join(OUTPUT_DIR, file_name), "w", encoding="utf-8") as f:
                    f.write(f"# {' / '.join(path_list)}\n\n{md_body}")
        except Exception as e:
            print(f"  [!] 抓取失败: {url} -> {e}")

    def run(self):
        self.driver.get(LOGIN_URL)
        input(">>> 请登录后按回车...")
        self.sync_cookies()
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            self.traverse_json(json.load(f))
        self.driver.quit()
        print(">>> 任务圆满完成！")

if __name__ == "__main__":
    DocScraper().run()
