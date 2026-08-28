# -*- coding: utf-8 -*-
import json, re, os

REPO = '/Users/ohadlevy/Projects/taavoura-binder'
FOLDER = '/Users/ohadlevy/Library/Mobile Documents/com~apple~CloudDocs/עבודה /תעבורה/מאגר פסיקה לקלסר/20 פסקי דין מקוריים שחסרו'

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
missing = [(k, v) for k, v in links.items() if not v or 'psika-north' not in v]
missing_index = {}
for k, v in missing:
    kk = key_of(k)
    if kk:
        missing_index.setdefault(kk, []).append(k)

files = [f for f in os.listdir(FOLDER) if not f.startswith('.') and f != 'סטטוס איתור.txt']
print('files:', len(files))

matches = []
unmatched_files = []
for f in files:
    stem = os.path.splitext(f)[0]
    kk = key_of(stem)
    if kk and kk in missing_index:
        for full_key in missing_index[kk]:
            matches.append({'file': f, 'full_key': full_key})
    else:
        unmatched_files.append(f)

print('matched:', len(matches))
for m in matches:
    print(' ', m['file'], '->', m['full_key'])
print('unmatched files:', unmatched_files)

json.dump(matches, open('/tmp/missing20_matches.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
