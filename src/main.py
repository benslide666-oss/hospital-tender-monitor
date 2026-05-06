import sys
from searcher import run_search
from emailer import send_email
from history import filter_new, save_history

def main():
    print("=" * 50)
    print("医院法务招标信息监控系统 启动")
    print("=" * 50)

    print("\n[1/3] 开始搜索招标信息...")
    try:
        tenders = run_search()
    except Exception as e:
        print(f"搜索阶段出错: {e}")
        sys.exit(1)

    print("\n[2/3] 历史去重过滤...")
    try:
        new_tenders = filter_new(tenders)
    except Exception as e:
        print(f"历史过滤出错: {e}")
        new_tenders = tenders

    print(f"\n[3/3] 发送邮件（共 {len(new_tenders)} 条新结果）...")
    try:
        send_email(new_tenders)
        # 发送成功后保存历史
        save_history({t["url"] for t in new_tenders if t.get("url")})
    except Exception as e:
        print(f"邮件发送出错: {e}")
        sys.exit(1)

    print("\n✅ 全部完成！")

if __name__ == "__main__":
    main()
