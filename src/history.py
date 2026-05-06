"""
历史去重模块
已推送的条目 URL 保存在 data/history.json
每次运行时过滤掉已推送过的，并更新记录
"""
import json, os
from datetime import datetime

HISTORY_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'history.json')

def load_history() -> set:
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return set(data.get('sent_urls', []))

def save_history(urls: set):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    existing = load_history()
    merged = existing | urls
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            'sent_urls': list(merged),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_count': len(merged),
        }, f, ensure_ascii=False, indent=2)
    print(f"历史记录已更新，累计 {len(merged)} 条")

def filter_new(items: list) -> list:
    sent = load_history()
    new_items = [i for i in items if i.get('url') not in sent]
    print(f"历史过滤：{len(items)} 条 → {len(new_items)} 条新结果")
    return new_items
