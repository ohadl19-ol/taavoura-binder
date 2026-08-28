import json
from bs4 import BeautifulSoup
raw = open('/Users/ohadlevy/Projects/taavoura-binder/index.html', encoding='utf-8').read()
soup = BeautifulSoup(raw, 'lxml')
slots = soup.select('.case-link-slot')
print('total case-link-slots:', len(slots))
bad = [s for s in slots if s.select('a.chip')]
print('slots with a baked chip (should be 0):', len(bad))
print('notion refs anywhere in html:', raw.count('app.notion.com'))

links = json.load(open('/Users/ohadlevy/Projects/taavoura-binder/links.json', encoding='utf-8'))
notion_vals = [k for k, v in links.items() if v and 'notion.com' in v]
empty_vals = [k for k, v in links.items() if not v]
print('links.json entries:', len(links))
print('notion values left:', len(notion_vals))
print('empty (no source) values:', len(empty_vals))
for k in empty_vals:
    print('  no-source:', k)
