# -*- coding: utf-8 -*-
import json

REPO = '/Users/ohadlevy/Projects/taavoura-binder'
VAULT_BASE = 'https://psika-north.vercel.app/files/'

results = json.load(open('/tmp/missing20_ids.json', encoding='utf-8'))
links = json.load(open(REPO + '/links.json', encoding='utf-8'))

updated = 0
for key, file_id in results.items():
    if key in links:
        links[key] = VAULT_BASE + file_id
        updated += 1
    else:
        print('WARN: key not found in links.json:', key)

json.dump(links, open(REPO + '/links.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('links.json updated:', updated)

remaining_no_file = [(k, v) for k, v in links.items() if not v or 'psika-north' not in v]
print('still without a vault file:', len(remaining_no_file))
for k, v in remaining_no_file:
    print(' ', k, '|', v or '(no link)')
