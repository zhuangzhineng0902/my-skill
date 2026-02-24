import os
import math
import json
import csv

def create_file(path, content):
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Created: {path}")

# --- 1. 核心 BM25 检索引擎 (Python 实现) ---
bm25_engine_code = """
import math
import re
import csv
import os

class BM25:
    def __init__(self, corpus, k1=1.5, b=0.75):
        self.corpus = corpus
        self.k1 = k1
        self.b = b
        self.doc_len = [len(doc) for doc in corpus]
        self.avgdl = sum(self.doc_len) / len(corpus)
        self.n = len(corpus)
        self.tf = []
        self.df = {}
        self.idf = {}
        self._initialize()

    def _initialize(self):
        for doc in self.corpus:
            tmp_tf = {}
            for word in doc:
                tmp_tf[word] = tmp_tf.get(word, 0) + 1
            self.tf.append(tmp_tf)
            for word in tmp_tf.keys():
                self.df[word] = self.df.get(word, 0) + 1
        for word, freq in self.df.items():
            self.idf[word] = math.log((self.n - freq + 0.5) / (freq + 0.5) + 1)

    def get_score(self, query, index):
        score = 0
        doc_tf = self.tf[index]
        for word in query:
            if word not in doc_tf: continue
            score += (self.idf[word] * doc_tf[word] * (self.k1 + 1) / 
                      (doc_tf[word] + self.k1 * (1 - self.b + self.b * self.doc_len[index] / self.avgdl)))
        return score

def tokenize(text):
    return re.findall(r'\\w+', text.lower())

def load_data(data_dir):
    documents = []
    metadata = []
    for filename in os.listdir(data_dir):
        if filename.endswith('.csv'):
            with open(os.path.join(data_dir, filename), 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    content = " ".join(row.values())
                    documents.append(tokenize(content))
                    metadata.append({"source": filename, "data": row})
    return documents, metadata

def search(query_str):
    data_dir = os.path.join(os.path.dirname(__file__), "../data")
    docs, meta = load_data(data_dir)
    bm25 = BM25(docs)
    query = tokenize(query_str)
    scores = [(bm25.get_score(query, i), i) for i in range(len(docs))]
    scores.sort(key=lambda x: x[0], reverse=True)
    
    results = []
    for score, index in scores[:5]: # 返回前5个最相关的规范
        if score > 0:
            item = meta[index]
            results.append(f"[Score: {score:.2f}] Source: {item['source']}\\nContent: {item['data']}\\n")
    return "\\n".join(results) if results else "No matching guidelines found."

if __name__ == "__main__":
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    print(search(query))
"""

# --- 2. 更加完整的规范数据 ---

# UX 交互红线
ux_guidelines = """Scenario,Rule,Priority,Detail
Validation,表单校验必须在失焦(Blur)时触发,High,减少用户输入时的干扰
Navigation,面包屑导航必须包含当前页面的父级路径,Medium,确保用户知道自己在哪里
Feedback,超过2秒的操作必须显示进度条而非静止Loading,Critical,缓解用户焦虑
Buttons,关键删除操作必须使用红色主题并带有二次确认,High,防止误删
"""

# 字体与排版
typography = """Token,FontFamily,Size,Weight,Usage
--font-h1,PingFang SC / Inter,32px,600,一级标题
--font-body,PingFang SC / Inter,14px,400,正文内容
--font-code,JetBrains Mono,12px,400,代码块/技术指标
"""

# 设计系统核心组件映射
components = """Component,Internal_Tag,Library,Status,Usage_Notes
Table,n-data-table,Nexus-UI,Ready,必须配置 row-key 和 virtual-scroll
Button,n-button,Nexus-UI,Ready,主按钮全局只能出现一个
Modal,n-modal,Nexus-UI,Ready,宽度建议固定为 520px/840px/1200px
"""

# 品牌颜色
brand = """Category,Token,Value,Usage
Brand,Primary,#0052D9,主要操作/链接
Status,Success,#2BA471,成功/在线
Status,Error,#D54941,报错/离线
Neutral,Border,#DCDCDC,边框颜色
"""

# --- 3. 生成 Skill 说明书 ---
skill_main = """# Enterprise UI/UX Engineering (BM25 Enabled)

你是一个集成了 **BM25 语义检索** 的企业级 UI/UX 专家 AI。

## 检索机制
你拥有一个基于 BM25 算法的检索工具 `search_engine.py`。
当用户要求设计页面或编写 UI 代码时，你**必须**：
1. 先提取用户需求中的关键词（如：表格、报错、主色调）。
2. 调用 `python3 .shared/enterprise-ui-skill/scripts/search_engine.py "<关键词>"`。
3. 根据返回的相关性评分（Score）最高的规范来生成代码。

## 核心设计哲学
- **Token First**: 严禁直接写 `color: #0052D9`，必须检索对应的 Token 如 `var(--brand-primary)`。
- **UX Consistency**: 严格遵守 `ux-guidelines.csv` 中的反馈与校验机制。
- **Library Compliance**: 仅使用内部 `Nexus-UI` 组件。
"""

def main():
    root = ".shared/enterprise-ui-skill"
    # 创建目录和文件
    create_file(f"{root}/data/ux_guidelines.csv", ux_guidelines)
    create_file(f"{root}/data/typography.csv", typography)
    create_file(f"{root}/data/components.csv", components)
    create_file(f"{root}/data/brand.csv", brand)
    
    create_file(f"{root}/scripts/search_engine.py", bm25_engine_code)
    create_file(f"{root}/skill-main.md", skill_main)
    
    # Cursor 规则配置
    cursor_rules = {
        "name": "Enterprise UI/UX Specialist",
        "instruction": f"Always query the BM25 search engine in {root}/scripts/search_engine.py before providing UI/UX solutions to ensure alignment with corporate standards."
    }
    create_file(".cursorrules", json.dumps(cursor_rules, indent=2))

    print("\n🚀 [高级版] 企业 UI/UX Skill 已生成，集成 BM25 检索算法！")

if __name__ == "__main__":
    main()
