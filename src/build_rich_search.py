# -*- coding: utf-8 -*-
import json, re
from bs4 import BeautifulSoup

REPO = '/Users/ohadlevy/Projects/taavoura-binder'
raw = open(REPO + '/index.html', encoding='utf-8').read()
soup = BeautifulSoup(raw, 'lxml')

HEADINGISH_CLASSES = {'case-title', 'topic-title'}

def norm(s):
    return re.sub(r'\s+', ' ', s or '').strip()

def is_heading(el):
    if getattr(el, 'name', None) != 'div':
        return False
    classes = set(el.get('class') or [])
    if classes & HEADINGISH_CLASSES:
        return True
    if 'subsection' in classes or 'chapter' in classes:
        return True
    return False

entries = []

# ---- existing chapter/subsection entries (broad topic-level, kept for fallback) ----
for el in soup.select('.chapter[id], .subsection[id]'):
    heading = el.select_one('.chapter-title, .sub-title')
    label = norm(heading.get_text(' ', strip=True)) if heading else norm(el.get('id'))
    text = norm(el.get_text(' ', strip=True))
    entries.append({'id': el.get('id'), 'type': 'chapter', 'label': label, 'text': text[:4000]})

# ---- case-title units: heading + following paragraphs until the next heading ----
for el in soup.select('.case-title[id]'):
    label = norm(el.get_text(' ', strip=True))
    parts = [label]
    sib = el.find_next_sibling()
    while sib is not None and not is_heading(sib):
        if sib.name == 'p':
            parts.append(norm(sib.get_text(' ', strip=True)))
        sib = sib.find_next_sibling()
    entries.append({'id': el.get('id'), 'type': 'case', 'label': label, 'text': norm(' '.join(parts))})

# ---- topic-title units: heading + following paragraphs until the next heading ----
for el in soup.select('.topic-title[id]'):
    label = norm(el.get_text(' ', strip=True))
    parts = [label]
    sib = el.find_next_sibling()
    while sib is not None and not is_heading(sib):
        if sib.name == 'p':
            parts.append(norm(sib.get_text(' ', strip=True)))
        sib = sib.find_next_sibling()
    entries.append({'id': el.get('id'), 'type': 'topic', 'label': label, 'text': norm(' '.join(parts))})

# ---- table row units ----
for tr in soup.select('tr[id]'):
    cells = [norm(td.get_text(' ', strip=True)) for td in tr.find_all('td')]
    label = cells[0] if cells else ''
    entries.append({'id': tr.get('id'), 'type': 'row', 'label': label, 'text': norm(' '.join(cells))})

print('total entries:', len(entries))
from collections import Counter
print(Counter(e['type'] for e in entries))

m = re.search(r'(<script id="search-index" type="application/json">)(.*?)(</script>)', raw, re.S)
new_json = json.dumps(entries, ensure_ascii=False)
raw2 = raw[:m.start(2)] + new_json + raw[m.end(2):]
open(REPO + '/index.html', 'w', encoding='utf-8').write(raw2)
print('written, size:', len(raw2))
