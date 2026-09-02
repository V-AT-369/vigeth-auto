import html
import os

try:
    text = open('tenders_digest.md', encoding='utf-8').read()
except FileNotFoundError:
    text = ''

parts = text.split('\n## ')
entries = parts[1:]
seen = set()
rows = []
for e in entries:
    lines = [l.strip() for l in e.strip().split('\n') if l.strip()]
    if not lines:
        continue
    title = lines[0]
    fields = {}
    for l in lines[1:]:
        if l.startswith('- ') and ':' in l:
            k, v = l[2:].split(':', 1)
            fields[k.strip()] = v.strip()
    buyer = fields.get('Buyer', '')
    key = (title, buyer)
    if key in seen:
        continue
    seen.add(key)
    deadline = fields.get('Deadline', 'None')
    value = fields.get('Estimated value', '')
    rows.append(
        "<tr>"
        f"<td style='padding:8px;border-bottom:1px solid #e5e5e5;font-weight:600;'>{html.escape(title)}</td>"
        f"<td style='padding:8px;border-bottom:1px solid #e5e5e5;'>{html.escape(buyer)}</td>"
        f"<td style='padding:8px;border-bottom:1px solid #e5e5e5;'>{html.escape(deadline)}</td>"
        f"<td style='padding:8px;border-bottom:1px solid #e5e5e5;'>{html.escape(value)}</td>"
        "</tr>"
    )

if rows:
    table_rows = "".join(rows)
    body = f"""<div style="font-family:Arial,sans-serif;font-size:14px;color:#222;">
<h2 style="margin-bottom:4px;">Vigeth Tenders &mdash; IT/Software Services Digest</h2>
<p style="color:#666;margin-top:0;">UK Find a Tender &middot; {len(rows)} unique opportunities</p>
<table style="border-collapse:collapse;width:100%;font-size:13px;">
<tr style="background:#f3f3f3;text-align:left;"><th style="padding:8px;">Title</th><th style="padding:8px;">Buyer</th><th style="padding:8px;">Deadline</th><th style="padding:8px;">Value (GBP)</th></tr>
{table_rows}
</table>
<p style="color:#888;font-size:12px;margin-top:16px;">Automated daily digest from your Vigeth Tenders pipeline (GitHub Actions, free tier).</p>
</div>"""
    count = str(len(rows))
else:
    body = "<p>No IT/software tenders were found in today's run.</p>"
    count = "0"

with open('email_body.html', 'w', encoding='utf-8') as f:
    f.write(body)

gh_env = os.environ.get('GITHUB_ENV')
if gh_env:
    with open(gh_env, 'a', encoding='utf-8') as f:
        f.write(f"TENDER_COUNT={count}\n")

print(f"Built email body with {count} unique tenders.")
