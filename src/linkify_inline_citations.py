# -*- coding: utf-8 -*-
import json, re

REPO = '/Users/ohadlevy/Projects/taavoura-binder'

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
    t = strip_quotes(text)
    m_type = TYPE_RE.search(t)
    m_num = NUM_RE.search(t)
    if not m_type or not m_num:
        return None
    return (m_type.group(1), norm_number(m_num.group(1)))

links = json.load(open(REPO + '/links.json', encoding='utf-8'))
by_norm = {}
for k, v in links.items():
    if not v:
        continue
    kk = key_of(k)
    if kk and kk not in by_norm:
        by_norm[kk] = v

raw = open(REPO + '/index.html', encoding='utf-8').read()

STRONG_RE = re.compile(r'<strong>(.*?)</strong>', re.S)
CASE_TITLE_PREFIX = '<div class="case-title">'

edits = []  # (start, end, replacement)
linked = 0
for m in STRONG_RE.finditer(raw):
    inner = m.group(1)
    if '<a ' in inner or '<a>' in inner:
        continue
    pre = raw[max(0, m.start() - len(CASE_TITLE_PREFIX)):m.start()]
    if pre == CASE_TITLE_PREFIX:
        continue  # already has its own case-link-slot button right after
    plain = re.sub(r'<[^>]+>', '', inner)
    kk = key_of(plain)
    if not kk or kk not in by_norm:
        continue
    url = by_norm[kk]
    replacement = (
        '<strong><a class="inline-case-link" href="' + url +
        '" target="_blank" rel="noopener">' + inner + '</a></strong>'
    )
    edits.append((m.start(), m.end(), replacement))
    linked += 1

print('inline citations to link:', linked)

for start, end, replacement in reversed(edits):
    raw = raw[:start] + replacement + raw[end:]

open(REPO + '/index.html', 'w', encoding='utf-8').write(raw)
print('done')
