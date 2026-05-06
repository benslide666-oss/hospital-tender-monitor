import smtplib, os, re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

def build_html_report(tenders: list) -> str:
    date_str = datetime.now().strftime("%Y年%m月%d日")

    if not tenders:
        body = "<p style='color:#888'>本周未检索到符合条件的招标信息。</p>"
    else:
        rows = ""
        for i, t in enumerate(tenders, 1):
            bg = "#f4f8ff" if i % 2 == 0 else "#ffffff"
            title_cell = (f'<a href="{t["url"]}" style="color:#1a5fa8;font-weight:bold;'
                          f'text-decoration:none;">{t["title"]}</a>'
                          if t.get("url") else f'<strong>{t["title"]}</strong>')
            summary = t.get("summary", "")
            amount  = t.get("amount", "")
            amount_html = (f'<span style="color:#c0392b;font-weight:bold">{amount}</span>'
                           if amount else '<span style="color:#ccc">—</span>')
            rows += f"""
            <tr style="background:{bg}">
              <td style="padding:10px 8px;border:1px solid #dce3ec;text-align:center;
                         color:#888;width:36px">{i}</td>
              <td style="padding:10px 12px;border:1px solid #dce3ec">
                {title_cell}
                <div style="font-size:12px;color:#666;margin-top:4px">{summary}</div>
              </td>
              <td style="padding:10px 8px;border:1px solid #dce3ec;text-align:center;
                         font-size:12px;width:90px">{t.get('date','')}</td>
              <td style="padding:10px 8px;border:1px solid #dce3ec;text-align:center;
                         font-size:12px;width:80px">{amount_html}</td>
              <td style="padding:10px 8px;border:1px solid #dce3ec;text-align:center;
                         font-size:12px;color:#555;width:120px">{t.get('source','')}</td>
            </tr>"""

        body = f"""
        <table style="border-collapse:collapse;width:100%;font-size:14px">
          <thead>
            <tr style="background:#1a5fa8;color:#fff">
              <th style="padding:10px 8px">#</th>
              <th style="padding:10px 12px;text-align:left">项目名称 / 摘要</th>
              <th style="padding:10px 8px">发布日期</th>
              <th style="padding:10px 8px">预算金额</th>
              <th style="padding:10px 8px">来源</th>
            </tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>"""

    return f"""
    <html><body style="font-family:'微软雅黑',Arial,sans-serif;color:#333;
                       max-width:960px;margin:0 auto;padding:20px">
      <div style="background:#1a5fa8;color:white;padding:18px 24px;border-radius:6px 6px 0 0">
        <h2 style="margin:0;font-size:20px">🏥 医院法务招标信息周报</h2>
        <p style="margin:6px 0 0;opacity:.85;font-size:13px">
          {date_str} · 覆盖江苏、浙江、上海、安徽</p>
      </div>
      <div style="border:1px solid #dce3ec;border-top:none;padding:20px;
                  border-radius:0 0 6px 6px">
        <p>本周共收录 <strong style="color:#1a5fa8">{len(tenders)}</strong>
           条医院法务相关招标信息（点击标题查看原文）：</p>
        {body}
        <hr style="margin-top:24px;border:none;border-top:1px solid #eee">
        <p style="font-size:12px;color:#aaa">
          由 GitHub Actions 定时任务自动发送 · 每周一汇总上周数据<br>
          数据来源：中国政府采购网、各省政府采购网、公共资源交易平台
        </p>
      </div>
    </body></html>"""

def send_email(tenders: list):
    user     = os.environ["EMAIL_USER"]
    password = os.environ["EMAIL_PASS"]
    target   = os.environ["TARGET_EMAIL"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = (f'【医院法务招标周报】{datetime.now().strftime("%Y-%m-%d")}'
                      f'｜江浙沪皖｜共{len(tenders)}条')
    msg["From"] = user
    msg["To"]   = target
    msg.attach(MIMEText(build_html_report(tenders), "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.qq.com", 465) as server:
        server.login(user, password)
        server.sendmail(user, [target], msg.as_string())
    print(f"✅ 邮件已发送至 {target}")
