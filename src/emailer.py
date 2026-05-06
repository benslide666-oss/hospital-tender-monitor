import smtplib, os, re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# 省份显示顺序
REGION_ORDER = ["江苏", "浙江", "上海", "安徽", "广东", "北京",
                "四川", "湖北", "山东", "河南", "湖南", "福建", "其他"]

def build_region_section(region: str, items: list) -> str:
    rows = ""
    for i, t in enumerate(items, 1):
        bg = "#f4f8ff" if i % 2 == 0 else "#ffffff"
        link = (f'<a href="{t["url"]}" style="color:#1a5fa8;font-weight:bold;text-decoration:none">'
                f'{t["title"]}</a>' if t.get("url") else f'<strong>{t["title"]}</strong>')
        summary = t.get("summary", "")
        amount  = t.get("amount", "")
        amount_html = (f'<span style="color:#c0392b;font-weight:bold">{amount}</span>'
                       if amount else '<span style="color:#ccc">—</span>')
        rows += f"""
        <tr style="background:{bg}">
          <td style="padding:9px 8px;border:1px solid #dce3ec;text-align:center;color:#888;width:32px">{i}</td>
          <td style="padding:9px 12px;border:1px solid #dce3ec">
            {link}
            <div style="font-size:12px;color:#666;margin-top:3px">{summary}</div>
          </td>
          <td style="padding:9px 8px;border:1px solid #dce3ec;text-align:center;font-size:12px;width:95px">{t.get('date','')}</td>
          <td style="padding:9px 8px;border:1px solid #dce3ec;text-align:center;font-size:12px;width:75px">{amount_html}</td>
          <td style="padding:9px 8px;border:1px solid #dce3ec;text-align:center;font-size:12px;color:#555;width:110px">{t.get('source','')}</td>
        </tr>"""

    return f"""
    <div style="margin-bottom:28px">
      <div style="background:#2c5f8a;color:white;padding:8px 16px;border-radius:4px 4px 0 0;
                  font-size:15px;font-weight:bold">
        📍 {region}（{len(items)} 条）
      </div>
      <table style="border-collapse:collapse;width:100%;font-size:14px">
        <thead>
          <tr style="background:#e8f0f8">
            <th style="padding:8px;border:1px solid #dce3ec">#</th>
            <th style="padding:8px;border:1px solid #dce3ec;text-align:left">项目名称 / 摘要</th>
            <th style="padding:8px;border:1px solid #dce3ec">发布日期</th>
            <th style="padding:8px;border:1px solid #dce3ec">预算金额</th>
            <th style="padding:8px;border:1px solid #dce3ec">来源</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
    </div>"""

def build_html_report(tenders: list) -> str:
    date_str = datetime.now().strftime("%Y年%m月%d日")

    # 按省份分组
    grouped = {}
    for t in tenders:
        r = t.get("region", "其他")
        grouped.setdefault(r, []).append(t)

    if not grouped:
        content = "<p style='color:#888'>本周未检索到符合条件的招标信息。</p>"
    else:
        # 生成目录
        toc_items = ""
        for region in REGION_ORDER:
            if region in grouped:
                toc_items += (f'<span style="margin-right:16px">'
                              f'<a href="#{region}" style="color:#1a5fa8;text-decoration:none">'
                              f'{region}（{len(grouped[region])}条）</a></span>')

        # 生成各省份区块
        sections = ""
        for region in REGION_ORDER:
            if region in grouped:
                sections += f'<div id="{region}">' + build_region_section(region, grouped[region]) + '</div>'

        content = f"""
        <div style="background:#f0f4f8;padding:12px 16px;border-radius:4px;margin-bottom:20px;font-size:13px">
          <strong>快速跳转：</strong> {toc_items}
        </div>
        {sections}"""

    return f"""
    <html><body style="font-family:'微软雅黑',Arial,sans-serif;color:#333;max-width:980px;margin:0 auto;padding:20px">
      <div style="background:#1a5fa8;color:white;padding:18px 24px;border-radius:6px 6px 0 0">
        <h2 style="margin:0;font-size:20px">🏥 医院法务招标信息周报</h2>
        <p style="margin:6px 0 0;opacity:.85;font-size:13px">
          {date_str} · 共 {len(tenders)} 条 · 覆盖12省市</p>
      </div>
      <div style="border:1px solid #dce3ec;border-top:none;padding:20px;border-radius:0 0 6px 6px">
        {content}
        <hr style="margin-top:24px;border:none;border-top:1px solid #eee">
        <p style="font-size:12px;color:#aaa">
          由 GitHub Actions 定时任务自动发送 · 每周一汇总<br>
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
                      f'｜12省市｜共{len(tenders)}条')
    msg["From"] = user
    msg["To"]   = target
    msg.attach(MIMEText(build_html_report(tenders), "html", "utf-8"))
    with smtplib.SMTP_SSL("smtp.qq.com", 465) as server:
        server.login(user, password)
        server.sendmail(user, [target], msg.as_string())
    print(f"✅ 邮件已发送至 {target}")
