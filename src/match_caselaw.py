# -*- coding: utf-8 -*-
import json, re, csv, os

REPO = '/Users/ohadlevy/Projects/taavoura-binder'
CL_DIR = '/Users/ohadlevy/Library/Mobile Documents/com~apple~CloudDocs/עבודה /תעבורה/מאגר פסיקה לקלסר'

def strip_quotes(s):
    return re.sub(r'["\'׳״]', '', s)

def norm_number(s):
    # unify separators to '-', strip spaces
    s = s.strip()
    s = s.replace('‏', '').replace('‎', '')
    s = re.sub(r'\s+', '', s)
    s = s.replace('/', '-')
    return s

TYPE_RE = re.compile(r'([א-ת]{1,4})')
NUM_RE = re.compile(r'(\d{1,6}[/\-]\d{1,3}(?:[/\-]\d{1,3})?)')

def key_of(text):
    """Return (type_norm, number_norm) tuple used for matching, or None."""
    t = strip_quotes(text)
    m_type = TYPE_RE.search(t)
    m_num = NUM_RE.search(t)
    if not m_type or not m_num:
        return None
    typ = m_type.group(1)
    num = norm_number(m_num.group(1))
    return (typ, num)

# ---- load existing links.json (68 current binder citations) ----
links = json.load(open(os.path.join(REPO, 'links.json'), encoding='utf-8'))
binder_index = {}
for full_key in links:
    k = key_of(full_key)
    if k:
        binder_index.setdefault(k, []).append(full_key)

print('binder citations:', len(links), '-> keyed:', len(binder_index))

# ---- load CSV index ----
rows = list(csv.DictReader(open(os.path.join(CL_DIR, 'אינדקס פסיקה.csv'), encoding='utf-8-sig')))
print('csv rows:', len(rows))

matched = []
unmatched_csv = []
for r in rows:
    k = key_of(r['הליך'])
    if k and k in binder_index:
        for full_key in binder_index[k]:
            matched.append({'full_key': full_key, 'csv': r})
    else:
        unmatched_csv.append(r)

print('matched to existing binder citations:', len(matched))
print('csv rows NOT matched to existing binder citation:', len(unmatched_csv))
print()
print('--- unmatched CSV entries (candidates for a new appendix) ---')
for r in unmatched_csv:
    print(' ', r['הליך'], '|', r['סטטוס'], '|', r['קובץ מקומי'])

json.dump(matched, open('/tmp/matched.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(unmatched_csv, open('/tmp/unmatched_csv.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# also report which binder citations had NO csv match at all (still on old external links)
matched_keys = {m['full_key'] for m in matched}
no_match = [fk for fk in links if fk not in matched_keys]
print()
print('binder citations with no local-file match (', len(no_match), '):')
for fk in no_match:
    print(' ', fk)
json.dump(no_match, open('/tmp/binder_no_local_match.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
