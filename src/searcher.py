import requests
from bs4 import BeautifulSoup
import time
import random
from datetime import datetime, timedelta

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

KEYWORDS = [
    "医院 法律顾问 招标",
    "医院 法务 招标",
    "卫生健康委 法律服务 采购",
    "医疗机构 律师事务所 招标",
    "医院 法律服务 政府采购",
]

def search_ccgp(keyword):
    results = []
    try:
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y:%m:%d")
        today = datetime.now().strftime("%Y:%m:%d")
        encoded_kw = requests.utils.quote(keyword)
        url = (f"https://search.ccgp.gov.cn/bxsearch?searchtype=1&bidSort=0"
               f"&kw={encoded_kw}&start_time={week_ago}&end_time={today}&timeType=6")
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "lxml")
        for item in soup.select("ul.vT-srch-result-list-bid li")[:10]:
            title_el = item.select_one("a")
            date_el = item.select_one("span.vT-srch-result-list-bid-time")
            if title_el:
                results.append({
                    "title": title_el.get_text(strip=True),
                    "url": title_el.get("href", ""),
                    "date": date_el.get_text(strip=True) if date_el else "",
                    "source": "中国政府采购网",
                })
        time.sleep(random.uniform(1.5, 3.0))
    except Exception as e:
        print(f"[CCGP] 搜索出错 [{keyword}]: {e}")
    return results

def deduplicate(items):
    seen, unique = set(), []
    for item in items:
        if item["title"] not in seen:
            seen.add(item["title"])
            unique.append(item)
    return unique

def run_search():
    all_results = []
    for kw in KEYWORDS:
        print(f"  → 搜索关键词: {kw}")
        all_results.extend(search_ccgp(kw))
    deduped = deduplicate(all_results)
    print(f"搜索完成，去重后共 {len(deduped)} 条")
    return deduped
