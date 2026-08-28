import json
from bs4 import BeautifulSoup

raw = open('/Users/ohadlevy/Projects/taavoura-binder/index.html', encoding='utf-8').read()
soup = BeautifulSoup(raw, 'lxml')
ch = soup.select_one('#c-appendix')
body = ch.select_one('.chapter-body')

items = []
children = list(body.children)
i = 0
cur = None
for el in children:
    if getattr(el, 'name', None) == 'div' and 'case-title' in (el.get('class') or []):
        if cur:
            items.append(cur)
        cur = {'case': el.get_text(strip=True), 'desc': ''}
    elif getattr(el, 'name', None) == 'p' and cur is not None and not cur['desc']:
        cur['desc'] = el.get_text(strip=True)

if cur:
    items.append(cur)

print(len(items))
for it in items:
    print(it['case'], '|', it['desc'][:90])

json.dump(items, open('/tmp/appendix_entries.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
