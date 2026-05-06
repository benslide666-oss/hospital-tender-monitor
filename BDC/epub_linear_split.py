import os
import re
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

EPUB_PATH = "BDC/威威的GPT单词本(8000词).epub"
TARGET_DIR = "BDC/DCB"

def main():
    if not os.path.exists(EPUB_PATH):
        print(f"❌ 错误：找不到文件 {EPUB_PATH}")
        return

    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
    else:
        for f in os.listdir(TARGET_DIR):
            if f.endswith(".md"): os.remove(os.path.join(TARGET_DIR, f))

    print("正在深入解析 EPUB 结构...")
    book = epub.read_epub(EPUB_PATH)
    
    # 1. 获取书的所有文档条目（按阅读顺序）
    spine_items = []
    for item_tuple in book.spine:
        # item_tuple 格式通常为 ('id', 'yes')
        item_id = item_tuple[0]
        item = book.get_item_with_id(item_id)
        if item and item.get_type() == ebooklib.ITEM_DOCUMENT:
            spine_items.append(item)

    # 2. 建立 章节文件名 -> 对应字母 的映射表
    # 先抓取目录
    toc_map = {}
    def walk_toc(items):
        for item in items:
            if isinstance(item, tuple): walk_toc(item)
            elif isinstance(item, list): walk_toc(item)
            elif hasattr(item, 'title'):
                title = item.title.strip().upper()
                # 寻找单个字母 A-Z
                match = re.search(r'(?<![A-Z])[A-Z](?![A-Z])', title)
                if match:
                    letter = match.group(0)
                    # 记录该字母起始的文件名
                    clean_href = item.href.split('#')[0]
                    if letter not in toc_map:
                        toc_map[clean_href] = letter
    walk_toc(book.toc)

    # 3. 线性遍历所有章节并归档
    current_letter = None
    count_dict = {}

    print(f"检测到目录映射: {toc_map}")

    for item in spine_items:
        href = item.get_name()
        
        # 如果当前章节在目录里标记了新字母，则切换输出文件
        if href in toc_map:
            current_letter = toc_map[href]
            print(f"➡️ 进入字母区: {current_letter}")

        if not current_letter:
            continue

        # 提取当前章节内容
        soup = BeautifulSoup(item.get_content(), 'html.parser')
        text = soup.get_text(separator='\n')
        
        # 简单格式化：单词加粗
        lines = text.split('\n')
        processed_text = ""
        for i, line in enumerate(lines):
            line = line.strip()
            if not line: continue
            if i + 1 < len(lines) and "分析词义" in lines[i+1]:
                processed_text += f"\n## {line}\n"
                count_dict[current_letter] = count_dict.get(current_letter, 0) + 1
            else:
                processed_text += line + "\n"

        # 写入文件
        file_path = os.path.join(TARGET_DIR, f"{current_letter}.md")
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(processed_text)

    print("\n🎉 拆分完成！统计如下：")
    for letter in sorted(count_dict.keys()):
        print(f" - {letter}.md: 约 {count_dict[letter]} 个单词")

if __name__ == "__main__":
    main()
