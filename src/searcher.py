import requests
import time
import os
import re

SERPER_API_KEY = os.environ["SERPER_API_KEY"]

# 经过验证有效的查询策略
QUERIES = [
    # 江浙沪皖 + 常年法律顾问（最精准）
    '江苏 医院 常年法律顾问 招标公告 2026',
    '浙江 医院 常年法律顾问 招标公告 2026',
    '上海 医院 常年法律顾问 招标公告 2026',
    '安徽 医院 常年法律顾问 招标公告 2026',
    # 法律服务采购
    '江苏 医院 法律服务 采购公告 2026',
    '浙江 医院 法律服务 采购公告 2026',
    '上海 医院 法律服务 采购公告 2026',
    '安徽 医院 法律服务 采购公告 2026',
    # 卫健委
    '江苏 卫健委 常年法律顾问 2026',
    '浙江 卫健委 常年法律顾问 2026',
    '上海 卫生健康委 法律顾问 2026',
    '安徽 卫健委 法律顾问 招标 2026',
    # 比选/竞争性谈判
    '江苏 医院 法律顾问 比选公告 2026',
    '浙江 医院 法律顾问 比选公告 2026',
    '江苏 医院 法律顾问 竞争性谈判 2026',
    '浙江 医院 法律顾问 竞争性谈判 2026',
]

# 标题或摘要必须同时满足：有法律词 + 有医疗词 + 有招标词
LEGAL_WORDS  = ["法律顾问", "法务", "法律服务", "常年法律", "律师", "法律咨询"]
MEDICAL_WORDS = ["医院", "卫健委", "卫生健康", "医疗", "医科大学", "疾控中心"]
TENDER_WORDS  = ["招标", "采购", "比选", "竞争性", "公告", "中标", "询价"]

# 排除词：标题含这些词直接过滤掉
EXCLUDE_WORDS = ["招聘", "人才", "岗位", "简历", "求职", "社招", "校招",
                 "设备", "耗材", "药品", "工程", "装修", "保洁", "物业",
                 "保安", "食堂", "餐饮", "停车", "绿化"]

def is_relevant(title: str, snippet: str) -> bool:
    text = title + snippet
    if any(w in title for w in EXCLUDE_WORDS):
        return False
    has_legal   = any(w in text for w in LEGAL_WORDS)
    has_medical = any(w in text for w in MEDICAL_WORDS)
    has_tender  = any(w in text for w in TENDER_WORDS)
    return has_legal and has_medical and has_tender

def extract_amount(text: str) -> str:
    for pattern in [r'[\d,]+\.?\d*\s*万元', r'预算[：:]\s*[\d,.]+', r'金额[：:]\s*[\d,.]+']:
        m = re.search(pattern, text)
        if m:
            return m.group()
    return ""

def extract_summary(snippet: str) -> str:
    """提取摘要中最有价值的一句"""
    sentences = [s.strip() for s in re.split(r'[。；\n·]', snippet) if len(s.strip()) > 10]
    for s in sentences:
        if any(w in s for w in LEGAL_WORDS + TENDER_WORDS):
            return s[:80]
    return sentences[0][:80] if sentences else snippet[:80]

SOURCE_MAP = {
    "ccgp.gov.cn":      "中国政府采购网",
    "js.gov.cn":        "江苏政府采购",
    "zj.gov.cn":        "浙江政府采购",
    "sh.gov.cn":        "上海政府采购",
    "ah.gov.cn":        "安徽政府采购",
    "ggzy.":            "公共资源交易",
    "lvxunlaw.com":     "律寻法律",
    "zhaobiao.cn":      "招标网",
    "bidcenter.com.cn": "招标投标平台",
    "yy120":            "医院官网",
    "srmyy.com":        "医院官网",
}

def get_source(url: str) -> str:
    for k, v in SOURCE_MAP.items():
        if k in url:
            return v
    return "政府网站" if ".gov.cn" in url else "招标平台"

def serper_search(query: str) -> list:
    results = []
    try:
        resp = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"},
            json={"q": query, "gl": "cn", "hl": "zh-cn", "num": 10, "tbs": "qdr:m"},
            timeout=15,
        )
        for item in resp.json().get("organic", []):
            title   = item.get("title", "").strip()
            url     = item.get("link", "")
            snippet = item.get("snippet", "").strip()
            date    = item.get("date", "")
            if not is_relevant(title, snippet):
                continue
            results.append({
                "title":   title,
                "url":     url,
                "date":    date,
                "summary": extract_summary(snippet),
                "amount":  extract_amount(snippet),
                "source":  get_source(url),
            })
        time.sleep(0.5)
    except Exception as e:
        print(f"  [错误] {query[:30]}: {e}")
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
    for i, q in enumerate(QUERIES, 1):
        print(f"  [{i}/{len(QUERIES)}] {q}")
        found = serper_search(q)
        if found:
            print(f"         ✓ {len(found)} 条")
        all_results.extend(found)
    deduped = deduplicate(all_results)
    print(f"\n完成，过滤去重后共 {len(deduped)} 条")
    return deduped
