import os
import json


def create_file(path, content):
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Created: {path}")


# ==========================================
# 1. 全维度设计系统数据 (CSV) - 采用 S_/O_ 分离逻辑
# ==========================================

# [色彩] brand.csv
brand_csv = """S_Keywords,S_Synonyms,O_Token,O_Hex,O_Pixso_Path
Primary Main,品牌色 主色 蓝色,AUI-Color-Primary,#0052D9,AUI/Color/Primary
Success Green,成功 完成 绿色,AUI-Color-Success,#2BA471,AUI/Color/Success
Error Red Danger,错误 报错 红色 危险,AUI-Color-Error,#D54941,AUI/Color/Error
Warning Orange,警告 提醒 橙色,AUI-Color-Warning,#E37318,AUI/Color/Warning
Text Main,正文 黑色 字体颜色,AUI-Text-900,#1C1C1C,AUI/Text/900
Bg Page,背景色 底色 灰色,AUI-Bg-Page,#F2F3F5,AUI/Bg/Page
"""

# [排版] typography.csv
typography_csv = """S_Keywords,O_Level,O_Size,O_Weight,O_LineHeight,O_Usage
Heading Large H1,Heading-L,32px,600,40px,大标题/看板数字
Heading Medium H2,Heading-M,24px,600,32px,页面标题/弹窗标题
Body Regular,Body-R,14px,400,22px,默认正文内容
Body Small,Body-S,12px,400,20px,辅助说明文字
"""

# [阴影] shadows.csv
shadows_csv = """S_Keywords,O_Level,O_Box_Shadow,O_Usage
Shadow Small,Shadow-S,0 2px 4px rgba(0,0,0,0.08),气泡/下拉菜单
Shadow Medium,Shadow-M,0 4px 12px rgba(0,0,0,0.12),卡片/浮层
Shadow Large,Shadow-L,0 8px 24px rgba(0,0,0,0.16),弹窗/抽屉
"""

# [图标与插画] assets.csv
assets_csv = """S_Keywords,S_Type,O_Asset_Key,O_Size,O_Usage
Search Icon,Icon,aui-icon-search,16px,搜索框内图标
Empty State,Illustration,aui-illus-empty,200px,暂无数据占位图
404 Error,Illustration,aui-illus-404,240px,页面未找到插画
"""

# [样式主题] themes.csv
themes_csv = """S_Keywords,O_Theme,O_Target_Token,O_Override_Hex
Dark Mode,Dark,AUI-Bg-Page,#141414
Dark Mode,Dark,AUI-Text-900,#FFFFFF
Compact Mode,Compact,AUI-Space-Base,4px
"""

# [组件] components.csv
components_csv = """S_Keywords,O_Tag,O_CSS_Blueprint,O_Interaction
Button Primary,aui-btn-primary,"display:flex; padding:8px 16px; border-radius:4px; background:#0052D9; color:#FFFFFF;","Hover时背景加深10%"
Input Field,aui-input,"display:flex; height:32px; border:1px solid #DCDCDC; padding:0 12px;","Focus时边框变蓝色"
Table Data,aui-table,"width:100%; border-radius:8px; border-collapse:collapse;","支持奇偶行变色"
"""

# [模版布局] templates.csv
templates_csv = """S_Keywords,O_Name,O_Structure,O_Layout_Engine
Admin Layout,Admin-Sidebar,"Sidebar(240px) + Header(64px) + Content","Grid"
Dashboard,Dashboard-Grid,"3-Column Cards Layout","Flex-Wrap"
Detail Page,Master-Detail,"Left List(300px) / Right Detail(Auto)","Flex"
"""

# [设计模式] design_patterns.csv
patterns_csv = """S_Keywords,O_Pattern,O_Logic,O_Components
Filter Table,Search-Filter-Pattern,顶部筛选+下方表格展示,Input+Select+Table
Wizard Form,Multi-Step-Form,分步提交任务引导,Steps+Form+ButtonGroup
"""

# [UX准则] ux_guidelines.csv
ux_rules_csv = """S_Keywords,O_Rule,O_Priority,O_UX_Note
Validation Error,报错必须在Input下方显示红字,High,减少用户认知负担
Delete Confirm,物理删除必须强制二次确认弹窗,Critical,防止不可逆操作
Loading State,操作超过500ms必须显示Loading,Medium,缓解系统延迟焦虑
"""

# [间距] spacing.csv
spacing_csv = """S_Keywords,O_Token,O_Value
Small Gap,Space-S,8px
Medium Gap,Space-M,16px
Large Gap,Space-L,24px
"""

# ==========================================
# 2. 增强型 BM25 检索引擎 (区分 S_ 检索与 O_ 输出)
# ==========================================
search_engine_script = """
import math, re, csv, os, sys

class BM25Engine:
    def __init__(self, corpus):
        self.n = len(corpus)
        self.avgdl = sum(len(d) for d in corpus) / self.n if self.n > 0 else 0
        self.tf, self.df, self.idf = [], {}, {}
        for doc in corpus:
            tmp_tf = {}
            for word in doc: tmp_tf[word] = tmp_tf.get(word, 0) + 1
            self.tf.append(tmp_tf)
            for word in tmp_tf.keys(): self.df[word] = self.df.get(word, 0) + 1
        for word, freq in self.df.items():
            self.idf[word] = math.log((self.n - freq + 0.5) / (freq + 0.5) + 1)

    def get_score(self, query, index):
        score = 0
        for word in query:
            if word not in self.tf[index]: continue
            tf = self.tf[index][word]
            score += self.idf[word] * (tf * 2.5) / (tf + 1.5 * (0.25 + 0.75 * len(self.tf[index]) / self.avgdl))
        return score

def search(query_str):
    data_dir = os.path.join(os.path.dirname(__file__), "../data")
    docs, meta = [], []
    for f in os.listdir(data_dir):
        if f.endswith(".csv"):
            with open(os.path.join(data_dir, f), 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # 仅提取 S_ 开头的字段参与 BM25 索引建模
                    search_content = " ".join([v for k, v in row.items() if k.startswith('S_')])
                    docs.append(re.findall(r'\\w+', search_content.lower()))
                    meta.append({"file": f, "data": row})

    engine = BM25Engine(docs)
    q = re.findall(r'\\w+', query_str.lower())
    scores = sorted([(engine.get_score(q, i), i) for i in range(len(docs))], reverse=True)

    res = []
    for s, i in scores[:8]: # 返回前8条相关规范
        if s > 0:
            # 仅输出 O_ 开头的规范载荷给 AI
            payload = {k: v for k, v in meta[i]['data'].items() if k.startswith('O_')}
            res.append(f"[Match Score: {s:.2f}] [Source: {meta[i]['file']}]\\nPayload: {payload}")

    return "\\n".join(res) if res else "No enterprise AUI specs matched."

if __name__ == "__main__":
    print(search(sys.argv[1] if len(sys.argv) > 1 else ""))
"""

# ==========================================
# 3. 终极全维度详细版 skill.md
# ==========================================
skill_md = """---
name: AUI-Precision-Architect-for-Pixso
description: |
  本 Skill 是企业级 AUI 设计系统的代码实施专家。其核心目标是根据用户业务描述，
  输出符合企业 UI/UX 规范的【纯 HTML/CSS 代码】，并确保该代码在 Pixso 等设计工具中能被完美还原和二次编辑。

  【核心价值】：
  1. 像素级还原：严格调用全维度 CSV 资产（色、字、影、模式等）。
  2. 导入优化：生成符合设计工具解析逻辑的 Flex 布局。
  3. 语义化检索：基于 BM25 算法区分搜索词与规范数值。
---

# Skill: AUI-Master-Architect

## 1. 任务背景与目标 (Context)
你生成的 HTML/CSS 代码将通过插件导入 Pixso。为了确保设计师可以直接在 Pixso 中利用“自动布局（Auto Layout）”和“设计变量（Styles）”，你产出的代码必须具备极高的物理精确度和结构清晰度。

## 2. 核心知识库 (Multi-Dimension Assets)
你必须运行检索脚本 `search_engine.py` 来调取以下层级的规范：
- **原子层**: `brand.csv`(色彩), `typography.csv`(字体), `shadows.csv`(阴影), `spacing.csv`(间距)。
- **视觉层**: `assets.csv`(图标/插画), `themes.csv`(样式主题)。
- **组件层**: `components.csv`(AUI标准组件结构)。
- **架构层**: `templates.csv`(页面骨架), `patterns.csv`(设计模式)。
- **逻辑层**: `ux_guidelines.csv`(交互约束)。

## 3. 设计工具适配规范 (Import Protocol)
- **布局引擎**: 必须优先使用 `display: flex`（对应 Pixso Auto Layout）。
- **物理单位**: 全量使用 `px`，禁止使用 rem/em。
- **色彩表达**: 必须使用 `brand.csv` 中的 `O_Hex` 物理值。
- **图层命名**: 为 HTML 标签添加具有语义的 `class` 名（如 `aui-card-header`）。
- **显式声明**: 即使是默认值（如圆角 0），也请显式写出 CSS。

## 4. 决策与执行流 (Decision Logic)
1. **关键词提取**: 从用户需求中提取功能（如：表格）、意图（如：报错提示）、环境（如：深色模式）。
2. **执行语义检索**: 调用脚本搜索关键词。
3. **数据映射**: 
   - 将 `O_Token` 映射为 CSS 注释。
   - 将 `O_Hex` / `O_Value` 写入 CSS 属性。
4. **组件装配**: 根据 `O_Pattern` 和 `O_Structure` 搭建 HTML 树。
5. **交互注入**: 检查 `ux_guidelines.csv` 是否有必须补全的辅助图层（如校验文字）。

## 5. 输出格式要求
### 板块一：[规范审计报告]
- 🎨 色彩资产: 使用了哪些 O_Hex。
- 📏 布局资产: 选用了哪个 O_Name 模版。
- 💡 UX 适配: 为何添加了特定的交互逻辑。

### 板块二：[纯净 HTML/CSS 代码块]
提供包含内联或 `<style>` 的标准 HTML 文件。

### 板块三：[Pixso 编辑指南]
说明导入后如何调整 Auto Layout 参数以达到最佳效果。
"""


# ==========================================
# 4. 自动化生成逻辑
# ==========================================
def main():
    root = ".shared/ffe-ui-ux-skill"
    # 创建所有数据文件
    data_map = {
        "brand.csv": brand_csv,
        "typography.csv": typography_csv,
        "shadows.csv": shadows_csv,
        "assets.csv": assets_csv,
        "themes.csv": themes_csv,
        "components.csv": components_csv,
        "templates.csv": templates_csv,
        "patterns.csv": patterns_csv,
        "ux_guidelines.csv": ux_rules_csv,
        "spacing.csv": spacing_csv
    }
    for filename, content in data_map.items():
        create_file(f"{root}/data/{filename}", content.strip())

    # 创建脚本与指令
    create_file(f"{root}/scripts/search_engine.py", search_engine_script.strip())
    create_file(f"{root}/skill.md", skill_md.strip())

    # 配置 Cursor
    cursor_rules = {
        "name": "AUI Pro Master (Design-to-Code)",
        "instruction": f"Strictly follow {root}/skill.md. Always run search_engine.py to fetch AUI physical values for Pixso-compatible HTML generation."
    }
    create_file(".cursorrules", json.dumps(cursor_rules, indent=2))

    print("\n" + "=" * 60)
    print("🚀 [全维度·工业级] AUI 设计系统 Skill 初始化成功！")
    print("=" * 60)
    print(f"数据资产: {root}/data/ (已覆盖字、色、形、模式等10个维度)")
    print(f"检索引擎: {root}/scripts/search_engine.py (基于 S_/O_ 分离逻辑)")
    print(f"核心指令: {root}/skill.md (针对设计工具导入深度优化)")
    print("=" * 60)


if __name__ == "__main__":
    main()
