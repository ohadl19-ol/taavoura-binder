# -*- coding: utf-8 -*-
import json, os, re, hashlib, uuid, requests

ENV = {}
for line in open('/Users/ohadlevy/psika-north/.env.local', encoding='utf-8'):
    line = line.strip()
    if not line or line.startswith('#') or '=' not in line:
        continue
    k, v = line.split('=', 1)
    ENV[k.strip()] = v.strip()

SUPABASE_URL = ENV['NEXT_PUBLIC_SUPABASE_URL']
SERVICE_KEY = ENV['SUPABASE_SERVICE_ROLE_KEY']
BUCKET = 'legal-files'
REST_HEADERS = {
    'apikey': SERVICE_KEY, 'Authorization': f'Bearer {SERVICE_KEY}',
    'Content-Type': 'application/json', 'Prefer': 'return=representation',
}

PDF_DIR = '/Users/ohadlevy/Library/Mobile Documents/com~apple~CloudDocs/עבודה /תעבורה/מאגר פסיקה לקלסר/מאגר פסיקה PDF'
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

def fetch_existing():
    r = requests.get(
        f'{SUPABASE_URL}/rest/v1/legal_files',
        headers={'apikey': SERVICE_KEY, 'Authorization': f'Bearer {SERVICE_KEY}'},
        params={'select': 'id,title,case_number,normalized_case_number,storage_path', 'deleted_at': 'is.null'},
    )
    r.raise_for_status()
    return r.json()

# ---- 1) build links.json key -> vault file id map ----
links = json.load(open(REPO + '/links.json', encoding='utf-8'))
key_to_id = {}
for k, v in links.items():
    if v and 'psika-north.vercel.app/files/' in v:
        file_id = v.rsplit('/', 1)[-1]
        kk = key_of(k)
        if kk:
            key_to_id[kk] = file_id

print('binder cases with a vault id:', len(key_to_id))

# ---- 2) match local PDF files to those ids ----
files = [f for f in os.listdir(PDF_DIR) if f.lower().endswith('.pdf')]
print('local pdf files:', len(files))

plan = []
unmatched = []
for f in files:
    stem = os.path.splitext(f)[0]
    kk = key_of(stem)
    if kk and kk in key_to_id:
        plan.append({'file': f, 'id': key_to_id[kk]})
    else:
        unmatched.append(f)

print('matched to a vault id:', len(plan))
print('unmatched local files:', len(unmatched))
for u in unmatched:
    print('  UNMATCHED:', u)

json.dump(plan, open('/tmp/replace_plan.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
