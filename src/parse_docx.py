# -*- coding: utf-8 -*-
import re, json
from bs4 import BeautifulSoup

html = open('/tmp/updated_binder.html', encoding='utf-8').read()
soup = BeautifulSoup(html, 'lxml')
body = soup.body or soup
all_top = list(body.find_all(recursive=False))

CASE_PREFIXES = [
    'בש"פ', 'בש״פ', 'ב"ש', 'ב״ש', 'רע"פ', 'רע״פ', 'עפ"ת', 'עפ״ת', 'עמ"ת', 'עמ״ת',
    'ע"ח', 'ע״ח', 'מ"ת', 'מ״ת', 'בש"ת', 'בש״ת', "פל\"א", 'פל״א', 'בג"ץ', 'בג״ץ',
    'תת"ע', 'תת״ע', 'עבש"ת', 'עבש״ת', 'רע"א', 'רע״א', 'ע"פ', 'ע״פ', 'בע"ם', 'בע״ם',
    'דנ"פ', 'דנ״פ', 'ה"פ', 'ה״פ', 'רע"ב', 'רע״ב',
]
CH_RE = re.compile(r'^(\d+)\s*\.\s*(.+)$')
SUB_RE = re.compile(r'^([א-ת])\s*\.\s*(.+)$')

def elem_text(el):
    t = el.get_text(' ', strip=True).replace('\xa0', ' ')
    return re.sub(r'\s+', ' ', t).strip()

def is_bold(el):
    strong = el.find('strong')
    return strong is not None and len(elem_text(strong)) >= max(1, len(elem_text(el)) - 2)

def looks_like_case(text):
    t = text.strip()
    return any(t.startswith(p) for p in CASE_PREFIXES)

def get_links(el):
    return [{'text': a.get_text(' ', strip=True), 'href': a['href']} for a in el.find_all('a', href=True)]

def is_link_only_para(el, links):
    if not links:
        return False
    txt = elem_text(el)
    link_text_total = sum(len(l['text']) for l in links)
    return link_text_total >= len(txt) - 3

# ---- locate body start (skip the TOC, which repeats the same headings unbolded/without a table) ----
start_idx = None
for i, el in enumerate(all_top):
    if el.name == 'p' and is_bold(el):
        m = CH_RE.match(elem_text(el))
        if m and m.group(1) == '1':
            nxt = all_top[i + 1] if i + 1 < len(all_top) else None
            if nxt is not None and nxt.name == 'table':
                start_idx = i
                break
if start_idx is None:
    raise SystemExit('could not locate body start')
elements = all_top[start_idx:]
print('body elements:', len(elements))

# ---- pass 1: flatten into raw typed items ----
raw = []
for el in elements:
    if el.name == 'table':
        raw.append({'type': 'table', 'html': str(el)})
        continue
    if el.name != 'p':
        continue
    text = elem_text(el)
    if not text:
        continue
    bold = is_bold(el)
    if bold:
        m = CH_RE.match(text)
        if m:
            raw.append({'type': 'chapter', 'num': m.group(1), 'title': m.group(2)})
            continue
        m = SUB_RE.match(text)
        if m:
            raw.append({'type': 'sub', 'letter': m.group(1), 'title': m.group(2)})
            continue
        if looks_like_case(text):
            raw.append({'type': 'case', 'text': text, 'links': get_links(el)})
            continue
        raw.append({'type': 'topic', 'text': text})
        continue
    links = get_links(el)
    if is_link_only_para(el, links):
        raw.append({'type': 'link', 'links': links})
    else:
        raw.append({'type': 'para', 'html': str(el), 'links': links})

print('raw items:', len(raw))
from collections import Counter
print(Counter(r['type'] for r in raw))

# ---- pass 2: group into case-blocks (case heading + its trailing paras/links until next heading-ish item) ----
HEADINGISH = {'chapter', 'sub', 'case', 'topic', 'table'}
grouped = []
i = 0
n = len(raw)
while i < n:
    item = raw[i]
    if item['type'] == 'case':
        links = list(item['links'])
        paras = []
        j = i + 1
        while j < n and raw[j]['type'] not in HEADINGISH:
            if raw[j]['type'] == 'link':
                links.extend(raw[j]['links'])
            else:
                links.extend(raw[j].get('links', []))
                paras.append(raw[j]['html'])
            j += 1
        # de-dup links by href, preserve order
        seen = set()
        dedup = []
        for l in links:
            if l['href'] not in seen:
                seen.add(l['href'])
                dedup.append(l)
        grouped.append({'type': 'case', 'text': item['text'], 'links': dedup, 'paras': paras})
        i = j
    elif item['type'] == 'link':
        i += 1  # stray link-only line with no preceding case; drop (rare)
    else:
        grouped.append(item)
        i += 1

print('grouped items:', len(grouped))

# ---- pass 3: build chapter/sub tree with blocks ----
chapters = []
cur_chapter = None
cur_sub = None

def blocks_target():
    return cur_sub['blocks'] if cur_sub is not None else cur_chapter['blocks']

for item in grouped:
    if item['type'] == 'chapter':
        cur_chapter = {'num': item['num'], 'title': item['title'], 'blocks': [], 'subs': []}
        chapters.append(cur_chapter)
        cur_sub = None
    elif item['type'] == 'sub':
        cur_sub = {'letter': item['letter'], 'title': item['title'], 'blocks': []}
        cur_chapter['subs'].append(cur_sub)
    elif item['type'] == 'table':
        blocks_target().append({'kind': 'table', 'html': item['html']})
    elif item['type'] == 'topic':
        blocks_target().append({'kind': 'topic', 'text': item['text']})
    elif item['type'] == 'para':
        blocks_target().append({'kind': 'para', 'html': item['html']})
    elif item['type'] == 'case':
        blocks = blocks_target()
        blocks.append({'kind': 'subhead', 'variant': 'case', 'text': item['text']})
        blocks.append({'kind': 'links', 'items': item['links']})
        for p in item['paras']:
            blocks.append({'kind': 'para', 'html': p})

print('chapters found:', len(chapters))
for c in chapters:
    print(' ', c['num'], c['title'], '| subs:', len(c['subs']), '| blocks:', len(c['blocks']))

json.dump(chapters, open('/tmp/chapters_raw.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('wrote /tmp/chapters_raw.json')
