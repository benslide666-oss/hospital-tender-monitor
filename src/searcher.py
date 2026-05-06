import requests
import time
import os
from datetime import datetime

SERPER_API_KEY = os.environ["SERPER_API_KEY"]

# 搜索关键词 - 覆盖江浙沪皖地区医院法务招标
QUERIES = [
    "江苏 医院 法律顾问 招标 2026",
    "浙江 医院 法律顾问 招标 2026",
    "上海 医院 法律顾问 招标 2026",
    "安徽 医院 法律顾问 招标 2026",
    "江苏 卫健委 法律服务 采购 2026",
    "浙江 卫健委 法律服务 采购 2026",
    "上海 卫生健康委 法律服务 招标 2026",
    "安徽 卫健委 法律服务 采购 2026",
    "江苏 三级医院 法务 招标公告 2026",
    "浙江 三级医院 法务 招标公告 2026",
    "site:ccgp.gov.cn 医院 法律顾问 江苏",
    "site:ccgp.gov.cn 医院 法律顾问 浙江",
    "site:ccgp.gov.cn 医院 法律顾问 上海",
    "site:ccgp.gov.cn 医院 法律顾问 安徽",
    "site:zfcg.czt.zj.gov.cn 医院 法律服务",
    "site:ggzy.江苏 医院 法律顾问",
]

# 重点关注的网站域名（用于标注来源）
SOURCE_MAP = {
    "ccgp.gov.cn": "中国政府采购网",
    "zfcg.czt.zj.gov.cn": "浙江政府采购网",
    "js.gov.cn": "江苏政府网",
    "sh.gov.cn": "上海政府网",
    "ah.gov.cn": "安徽政府网",
    "ggzy": "公共资源交易平台",
    "bidcenter": "招标投标平台",
    "hospital": "医院官网",
    "yy120": "医院网站",
}

def get_source_label(url: str) -> str:
    for keyword, label in SOURCE_MAP.items():
        if keyword in url:
            return label
    return "招标平台"

def serper_search(query: str) -> list:
    results = []
    try:
        resp = requests.post(
            "https://google.serper.dev/search",
            headers={
                "X-API-KEY": SERPER_API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "q": query,
                "gl": "cn",
                "hl": "zh-cn",
                "num": 10,
                "tbs": "qdr:w",  # 只搜索最近一周
            },
            timeout=15,
        )
        data = resp.json()

        for item in data.get("organic", []):
            title = item.get("title", "").strip()
            url = item.get("link", "")
            snippet = item.get("snippet", "")
            date = item.get("date", "")

            # 过滤明显不相关的结果
            keywords = ["招标", "采购", "法律", "法务", "顾问", "公告"]
            if not any(k in title + snippet for k in keywords):
                continue

            results.append({
                "title": title,
                "url": url,
                "date": date,
                "snippet": snippet,
                "source": get_source_label(url),
            })

        time.sleep(0.5)

    except Exception as e:
        print(f"  [Serper] 搜索出错 [{query}]: {e}")

    return results


def deduplicate(items: list) -> list:
    seen, unique = set(), []
    for item in items:
        key = item["url"] or item["title"]
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


def run_search() -> list:
    all_results = []
    total = len(QUERIES)
    for i, query in enumerate(QUERIES, 1):
        print(f"  [{i}/{total}] 搜索: {query}")
        results = serper_search(query)
        print(f"         找到 {len(results)} 条")
        all_results.extend(results)

    deduped = deduplicate(all_results)
    print(f"\n搜索完成，去重后共 {len(deduped)} 条")
    return deduped
