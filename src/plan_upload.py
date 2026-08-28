# -*- coding: utf-8 -*-
import json, os, re

CL_DIR = '/Users/ohadlevy/Library/Mobile Documents/com~apple~CloudDocs/עבודה /תעבורה/מאגר פסיקה לקלסר'
PDF_DIR = '/tmp/pesika_pdf'

def slugify(name):
    return re.sub(r'\s+', '-', name.strip())

def resolve_source(rel_local_path):
    """Return (abs_path, ext, mime, original_filename) for the file to actually upload."""
    src = os.path.join(CL_DIR, rel_local_path)
    base = os.path.basename(rel_local_path)
    stem, ext = os.path.splitext(base)
    ext = ext.lower().lstrip('.')
    safe_stem = slugify(stem)
    if ext == 'pdf':
        return src, 'pdf', 'application/pdf', base
    if ext == 'doc':
        return src, 'doc', 'application/msword', base
    if ext in ('txt', 'html'):
        conv = os.path.join(PDF_DIR, safe_stem + '.pdf')
        return conv, 'pdf', 'application/pdf', stem + '.pdf'
    return None, None, None, None

items = []

matched = json.load(open('/tmp/matched.json', encoding='utf-8'))
for m in matched:
    row = m['csv']
    if not row['קובץ מקומי']:
        continue
    src, ext, mime, orig = resolve_source(row['קובץ מקומי'])
    items.append({
        'key': m['full_key'],
        'source': 'matched',
        'case_number': row['הליך'],
        'title': m['full_key'],
        'local_src': src, 'ext': ext, 'mime': mime, 'orig_filename': orig,
    })

appendix = json.load(open('/tmp/appendix.json', encoding='utf-8'))
for a in appendix:
    src, ext, mime, orig = resolve_source(a['local'])
    items.append({
        'key': 'APPX::' + a['case'],
        'source': 'appendix',
        'case_number': a['case'],
        'title': a['case'],
        'local_src': src, 'ext': ext, 'mime': mime, 'orig_filename': orig,
    })

missing = [it for it in items if not it['local_src'] or not os.path.isfile(it['local_src'])]
ok = [it for it in items if it['local_src'] and os.path.isfile(it['local_src'])]

print('total planned:', len(items))
print('ok (file exists):', len(ok))
print('missing:', len(missing))
for m in missing:
    print(' MISSING:', m['key'], '|', m['local_src'])

json.dump(ok, open('/tmp/upload_plan.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
