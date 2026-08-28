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
    if v and 'psika-north.vercel.app' in v:
        kk = key_of(k)
        if kk and kk not in by_norm:
            by_norm[kk] = v

raw = open(REPO + '/index.html', encoding='utf-8').read()
A_TAG_RE = re.compile(r'<a\s+([^>]*?)href="([^"]*)"([^>]*)>(.*?)</a>', re.S)
tags = list(A_TAG_RE.finditer(raw))
print('total <a> tags:', len(tags))

# group ANY consecutive touching <a> tags regardless of href
groups = []
i = 0
while i < len(tags):
    j = i
    end_pos = tags[i].end()
    while j + 1 < len(tags) and raw[end_pos:tags[j + 1].start()] == '':
        j += 1
        end_pos = tags[j].end()
    groups.append(tags[i:j + 1])
    i = j + 1

fixed_groups = 0
fixed_tags = 0
edits = []
for group in groups:
    if all('psika-north.vercel.app' in m.group(2) for m in group):
        continue  # already fully vault-linked
    combined_inner = ''.join(m.group(4) for m in group)
    plain = re.sub(r'<[^>]+>', '', combined_inner)
    kk = key_of(plain)
    if not kk or kk not in by_norm:
        continue
    new_url = by_norm[kk]
    start = group[0].start()
    end = group[-1].end()
    new_html = ''.join(
        '<a ' + m.group(1) + 'href="' + new_url + '"' + m.group(3) + '>' + m.group(4) + '</a>'
        for m in group
    )
    edits.append((start, end, new_html))
    fixed_groups += 1
    fixed_tags += len(group)

for start, end, new_html in reversed(edits):
    raw = raw[:start] + new_html + raw[end:]

print('groups fixed:', fixed_groups, '| tags touched:', fixed_tags)
open(REPO + '/index.html', 'w', encoding='utf-8').write(raw)
