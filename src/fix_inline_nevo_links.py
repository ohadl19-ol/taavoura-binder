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

# match any <a ...href="URL"...>TEXT</a> where URL is NOT already a vault link,
# and TEXT (stripped of tags) looks like a case citation we have a vault link for.
A_RE = re.compile(r'<a\s+([^>]*?)href="([^"]*)"([^>]*)>(.*?)</a>', re.S)

count = 0
def repl(m):
    global count
    pre_attrs, href, post_attrs, inner = m.groups()
    if 'psika-north.vercel.app' in href:
        return m.group(0)  # already correct
    plain = re.sub(r'<[^>]+>', '', inner)
    kk = key_of(plain)
    if not kk or kk not in by_norm:
        return m.group(0)
    new_url = by_norm[kk]
    count += 1
    return '<a ' + pre_attrs + 'href="' + new_url + '"' + post_attrs + '>' + inner + '</a>'

raw2 = A_RE.sub(repl, raw)
print('inline links redirected to vault:', count)
open(REPO + '/index.html', 'w', encoding='utf-8').write(raw2)
