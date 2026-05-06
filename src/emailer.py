import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

def build_html_report(tenders):
    date_str = datetime.now().strftime("%Y年%m月%d日")
    rows = ""
    for i, t in enumerate(tenders, 1):
        bg = "#f4f8ff" if i % 2 == 0 else "#ffffff"
        link = f'<a href="{t["url"]}">{t["title"]}</a>' if t.get("url") else t["title"]
        rows += f'<tr style="background:{bg}"><td style="padding:8px;border:1px solid #dce3ec;text-align:center">{i}</td><td style="padding:8px;border:1px solid #dce3ec">{link}</td><td style="padding:8px;border:1px solid #dce3ec;text-align:center">{t.get("date","")}</td><td style="padding:8px;border:1px solid #dce3ec;text-align:center">{t.get("source","")}</td></tr>'
    body = f'<table style="border-collapse:collapse;width:100%"><thead><tr style="background:#1a5fa8;color:#fff"><th style="padding:10px">序号</th><th style="padding:10px;text-align:left">项目名称</th><th style="padding:10px">发布日期</th><th style="padding:10px">来源</th></tr></thead><tbody>{rows}</tbody></table>' if tenders else "<p>本周未检索到相关招标信息。</p>"
    return f'<html><body style="font-family:Arial,sans-serif;max-width:900px;margin:0 auto;padding:20px"><div style="background:#1a5fa8;color:white;padding:18px 24px;border-radius:6px 6px 0 0"><h2 style="margin:0">🏥 医院法务招标信息周报</h2><p style="margin:6px 0 0;opacity:.85;font-size:13px">{date_str}</p></div><div style="border:1px solid #dce3ec;border-top:none;padding:20px;border-radius:0 0 6px 6px"><p>本周共收录 <strong style="color:#1a5fa8">{len(tenders)}</strong> 条招标信息：</p>{body}<hr style="margin-top:24px;border:none;border-top:1px solid #eee"><p style="font-size:12px;color:#aaa">由 GitHub Actions 自动发送，每周一汇总</p></div></body></html>'

def send_email(tenders):
    user = os.environ["EMAIL_USER"]
    password = os.environ["EMAIL_PASS"]
    target = os.environ["TARGET_EMAIL"]
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f'【医院法务招标周报】{datetime.now().strftime("%Y-%m-%d")}｜共{len(tenders)}条'
    msg["From"] = f"招标监控 <{user}>"
    msg["To"] = target
    msg.attach(MIMEText(build_html_report(tenders), "html", "utf-8"))
    with smtplib.SMTP_SSL("smtp.qq.com", 465) as server:
        server.login(user, password)
        server.sendmail(user, [target], msg.as_string())
    print(f"邮件已发送至 {target}")
