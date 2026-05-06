import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

# 配置路径
EPUB_PATH = "BDC/威威的GPT单词本(8000词).epub"
TARGET_DIR = "BDC/DCB"

def main():
    if not os.path.exists(EPUB_PATH):
        print(f"❌ 错误：找不到文件 {EPUB_PATH}")
        return

    # 1. 创建目录并清理
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
    for f in os.listdir(TARGET_DIR):
        if f.endswith(".md"):
            os.remove(os.path.join(TARGET_DIR, f))

    # 2. 读取 EPUB
    print("正在通过目录索引解析 EPUB...")
    book = epub.read_epub(EPUB_PATH)
    
    # 3. 解析目录 (TOC)
    # 我们寻找标题为 A, B, C... 或 目录A, 目录B... 的项
    toc_items = []
    
    def walk_toc(items):
        for item in items:
            if isinstance(item, tuple):
                walk_toc(item)
            elif isinstance(item, list):
                walk_toc(item)
            elif hasattr(item, 'title'):
                toc_items.append(item)

    walk_toc(book.toc)

    # 4. 按目录顺序提取并写入
    current_letter = None
    
    for item in toc_items:
        title = item.title.strip().upper()
        
        # 匹配目录标题，例如 "A", "目录A", "Section A"
        # 我们寻找标题中包含单个 A-Z 字母的情况
        match = re.search(r'(?<![A-Z])[A-Z](?![A-Z])', title)
        if match:
            current_letter = match.group(0)
            print(f"📍 正在处理目录: {title} -> {current_letter}.md")
        
        if not current_letter:
            continue

        # 获取目录对应的文档内容
        # item.href 格式通常为 "chapter1.xhtml#anchor"
        file_name = item.href.split('#')[0]
        doc = book.get_item_with_href(file_name)
        
        if doc:
            soup = BeautifulSoup(doc.get_content(), 'html.parser')
            # 简单清洗文本：去除多余空行，保持单词条目结构
            text = soup.get_text(separator='\n')
            
            # 将 HTML 转化为 Markdown 风格（这里做简单加粗处理）
            # 假设单词名在每一块的开头，我们将其转为 ## 标题
            processed_text = ""
            lines = text.split('\n')
            for i, line in enumerate(lines):
                line = line.strip()
                if not line: continue
                # 如果下一行包含“分析词义”，则认为本行是单词名
                if i+1 < len(lines) and "分析词义" in lines[i+1]:
                    processed_text += f"\n## {line}\n"
                else:
                    processed_text += line + "\n"

            # 写入对应的字母文件
            file_path = os.path.join(TARGET_DIR, f"{current_letter}.md")
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(processed_text + "\n\n---\n")

    print(f"\n🎉 任务完成！请在 {TARGET_DIR} 目录下查看 A-Z.md 文件。")

import re
if __name__ == "__main__":
    main()
