import os


def create_file(path, content):
    # 获取目录路径
    directory = os.path.dirname(path)
    # 只有当目录名不为空时才创建文件夹
    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ 已创建: {path}")


# --- 1. 定义企业 UI 规范数据 (CSV) ---
colors_csv = """Category,Name,Hex,Usage,Contrast_Rule
Primary,Brand-Main,#0052D9,主要按钮、激活状态,White Text
Success,Standard-Green,#2BA471,成功提示、完成进度,White Text
Warning,Alert-Orange,#E37318,警告信息、待办提醒,Dark Text
Error,Critical-Red,#D54941,错误提示、删除操作,White Text
Background,Page-Bg,#F2F3F5,整个页面的底色,N/A
Border,Component-Border,#DCDCDC,输入框、分割线颜色,N/A
"""

components_csv = """Component,Internal_Tag,Library_Source,Props_Guideline,Best_Practice
Button,n-button,Nexus-UI,"theme='primary' | 'strong'","提交类操作必须使用 'strong'"
Table,n-data-table,Nexus-UI,"size='large', :bordered='false'","数据超10条必须开启 virtual-scroll"
Modal,n-modal,Nexus-UI,"width='600px', :mask-closable='false'","弹窗底部按钮必须右对齐"
Form,n-form,Nexus-UI,"label-placement='left'","所有必填项必须带有星号标记"
"""

# --- 2. 定义 AI 检索逻辑脚本 (Python) ---
search_script = """import csv
import sys
import os

# 获取当前脚本所在目录的绝对路径，确保能找到 data 文件夹
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

def search_specs(keyword):
    results = []
    try:
        # 检索颜色
        with open(os.path.join(DATA_DIR, "brand-colors.csv"), 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if keyword.lower() in str(row).lower():
                    results.append(f"[Color] {row['Name']}: {row['Hex']} ({row['Usage']})")

        # 检索组件
        with open(os.path.join(DATA_DIR, "components.csv"), 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if keyword.lower() in str(row).lower():
                    results.append(f"[Component] {row['Internal_Tag']}: {row['Props_Guideline']}")
    except Exception as e:
        return f"Error reading specs: {str(e)}"

    return "\\n".join(results) if results else "No specific enterprise rule found."

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    print(search_specs(query))
"""

# --- 3. 定义 Skill 核心指令 (Markdown) ---
skill_main = """# Enterprise UI/UX Engineering Skill

## Role
你现在是【企业内部前端专家】，负责确保所有生成的 Web 页面严格符合公司《Nexus-UI 视觉交互规范》。

## Workflow
1. **分析需求**：识别用户描述的功能模块（如：列表页、表单页、看板）。
2. **规范查询**：在生成代码前，先查阅 .shared/enterprise-ui-skill/data/ 下的文件或运行检索脚本。
3. **代码生成**：
   - 必须使用 `Nexus-UI` 组件库标签。
   - 严禁硬编码颜色值，必须使用规范中的 Hex 或 CSS 变量。
   - 遵循 8px 栅格系统（padding/margin 必须是 8 的倍数）。

## UI Checklist (必须遵守)
- 页面左右内边距统一为 24px。
- 卡片（Card）的圆角统一为 4px。
- 按钮组中，“确定”在右，“取消”在左。
"""

# --- 4. 配置文件 ---
cursor_rules = """{
  "name": "Enterprise-UI-UX-Pro-Max",
  "rules": [
    "Before generating UI code, always check .shared/enterprise-ui-skill/data/ for brand guidelines.",
    "Use standard company colors and components as defined in the skill files."
  ]
}
"""


def main():
    # 路径定义
    base_dir = ".shared/enterprise-ui-skill"

    # 执行文件创建
    create_file(f"{base_dir}/data/brand-colors.csv", colors_csv)
    create_file(f"{base_dir}/data/components.csv", components_csv)
    create_file(f"{base_dir}/scripts/search_enterprise.py", search_script)
    create_file(f"{base_dir}/skill-main.md", skill_main)
    create_file(".cursorrules", cursor_rules)

    print("\n🚀 [成功] 企业 UI/UX Skill 工程代码已生成！")
    print("--------------------------------------------------")
    print(f"1. 规范数据存放于: {base_dir}/data/")
    print(f"2. 检索脚本存放于: {base_dir}/scripts/")
    print(f"3. AI 指令说明书: {base_dir}/skill-main.md")
    print("--------------------------------------------------")


if __name__ == "__main__":
    main()