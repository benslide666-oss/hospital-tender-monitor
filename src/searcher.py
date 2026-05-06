import requests, time, os, re

SERPER_API_KEY = os.environ["SERPER_API_KEY"]

QUERIES = [
    '江苏 医院 常年法律顾问 招标公告 2026',
    '浙江 医院 常年法律顾问 招标公告 2026',
    '上海 医院 常年法律顾问 招标公告 2026',
    '安徽 医院 常年法律顾问 招标公告 2026',
    '江苏 医院 法律服务 采购公告 2026',
    '浙江 医院 法律服务 采购公告 2026',
    '上海 医院 法律服务 采购公告 2026',
    '安徽 医院 法律服务 采购公告 2026',
    '江苏 卫健委 法律顾问 招标 2026',
    '浙江 卫健委 法律顾问 招标 2026',
    '江苏 医院 法律顾问 比选公告 2026',
    '浙江 医院 法律顾问 比选公告 2026',
]

LEGAL_WORDS  = ["法律顾问", "法务", "法律服务", "常年法律", "律师"]
MEDICAL_WORDS = ["医院", "卫健委", "卫生健康", "医疗", "医科大学",
                 "疾控", "卫生院", "诊疗", "省级机关", "医学院"]
TENDER_WORDS  = ["招标", "采购", "比选", "竞争性", "公告", "中标", "询价", "成交"]
EXCLUDE_WORDS = ["招聘", "人才", "岗位", "求职", "设备", "耗材",
                 "药品", "工程", "装修", "保洁", "物业", "食堂"]

def is_relevant(title, snippet):
    text = title + snippet
    if any(w in title for w in EXCLUDE_WORDS):
        return False
    return (any(w in text for w in LEGAL_WORDS) and
            any(w in text for w in MEDICAL_WORDS) and
            any(w in text for w in TENDER_WORDS))

def extract_amount(text):
    for p in [r'[\d,]+\.?\d*\s*万元', r'预算[：:]\s*[\d,.]+', r'金额[：:]\s*[\d,.]+']:
        m = re.search(p, text)
        if m:
            return m.group()
    return ""

def extract_summary(snippet):
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
    "chinabidding":     "中国招标",
    "jianyu360":        "剑鱼标讯",
    "yycg.":            "医院采购网",
}

def get_source(url):
    for k, v in SOURCE_MAP.items():
        if k in url:
            return v
    return "政府网站" if ".gov.cn" in url else "招标平台"

def serper_search(query):
    results = []
    try:
        resp = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"},
            json={"q": query, "gl": "cn", "hl": "zh-cn", "num": 10},  # 不限时间
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

def deduplicate(items):
    seen, unique = set(), []
    for item in items:
        key = item["url"] or item["title"]
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique

def run_search():
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
