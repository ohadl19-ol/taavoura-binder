# -*- coding: utf-8 -*-
import json, re

REPO = '/Users/ohadlevy/Projects/taavoura-binder'
links = json.load(open(REPO + '/links.json', encoding='utf-8'))

def strip_quotes(s):
    return re.sub(r'["\'׳״]', '', s)

def norm_number(s):
    s = s.strip()
    s = re.sub(r'\s+', '', s)
    s = s.replace('/', '-')
    return s

TYPE_RE = re.compile(r'([א-ת]{1,4})')
NUM_RE = re.compile(r'(\d{1,6}[/\-]\d{1,3}(?:[/\-]\d{1,3})?)')

def key_of(text):
    if not text:
        return None
    t = strip_quotes(text)
    m_type = TYPE_RE.search(t)
    m_num = NUM_RE.search(t)
    if not m_type or not m_num:
        return None
    return (m_type.group(1), norm_number(m_num.group(1)))

used_keys = set()
for k in links:
    kk = key_of(k)
    if kk:
        used_keys.add(kk)
print('used case-number keys in binder:', len(used_keys))

rows = json.load(open(REPO + '/src/notion_rows.json', encoding='utf-8'))
print('rows loaded:', len(rows))

candidates = []
for r in rows:
    erka = r.get('ערכאה') or ''
    if 'עליון' not in erka and 'מחוזי' not in erka:
        continue
    if r.get('סטטוס תקציר') != 'מלא':
        continue
    kk = key_of(r.get('מספר הליך'))
    if kk and kk in used_keys:
        continue  # already in binder
    if not r.get('קטגוריות עבירה'):
        continue
    candidates.append(r)

print('candidate rows (elyon/mechozi, מלא, not yet used):', len(candidates))
from collections import defaultdict
by_cat = defaultdict(list)
for r in candidates:
    cats = json.loads(r['קטגוריות עבירה']) if isinstance(r['קטגוריות עבירה'], str) else r['קטגוריות עבירה']
    for c in (cats or ['(ללא קטגוריה)']):
        by_cat[c].append(r)

for cat, items in sorted(by_cat.items(), key=lambda x: -len(x[1])):
    print()
    print('===', cat, '(', len(items), ') ===')
    for it in items:
        print(' ', it['ערכאה'][:20], '|', it['מספר הליך'], '|', (it.get('הלכה / תמצית') or '')[:90])
