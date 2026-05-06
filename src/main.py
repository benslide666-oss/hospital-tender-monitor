import sys
from searcher import run_search
from emailer import send_email

def main():
    print("=" * 50)
    print("医院法务招标信息监控系统 启动")
    print("=" * 50)
    print("\n[1/2] 开始搜索招标信息...")
    try:
        tenders = run_search()
    except Exception as e:
        print(f"搜索阶段出错: {e}")
        sys.exit(1)
    print(f"\n[2/2] 准备发送邮件（共 {len(tenders)} 条）...")
    try:
        send_email(tenders)
    except Exception as e:
        print(f"邮件发送出错: {e}")
        sys.exit(1)
    print("\n完成！")

if __name__ == "__main__":
    main()
