# -*- coding: utf-8 -*-
import json, html as htmlmod, os

REPO = '/Users/ohadlevy/Projects/taavoura-binder'
VAULT_BASE = 'https://psika-north.vercel.app/files/'

vault_ids = json.load(open('/tmp/vault_ids.json', encoding='utf-8'))

# ---- 1) links.json: point matched (non-APPX) keys to vault urls ----
links = json.load(open(os.path.join(REPO, 'links.json'), encoding='utf-8'))
updated = 0
for key, info in vault_ids.items():
    if key.startswith('APPX::'):
        continue
    if key in links:
        links[key] = VAULT_BASE + info['id']
        updated += 1
json.dump(links, open(os.path.join(REPO, 'links.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('links.json updated:', updated)

# ---- 2) index.html: replace pesika/... hrefs in the appendix chapter with vault urls ----
idx_path = os.path.join(REPO, 'index.html')
raw = open(idx_path, encoding='utf-8').read()

appendix = json.load(open('/tmp/appendix.json', encoding='utf-8'))
replaced = 0
for a in appendix:
    key = 'APPX::' + a['case']
    if key not in vault_ids:
        continue
    vault_url = VAULT_BASE + vault_ids[key]['id']
    old_href_attr = 'href="pesika/'  # will locate by case's data-case + nearby href
    # find this case's case-link-slot block and swap its chip href
    data_case = htmlmod.escape(a['case'], quote=True)
    marker = f'<div class="case-link-slot" data-case="{data_case}">'
    idx = raw.find(marker)
    if idx == -1:
        print('WARN: slot not found for', a['case'])
        continue
    end = raw.find('</div>', idx)
    block = raw[idx:end]
    # replace the href="pesika/...redirect" inside this block only
    import re as _re
    new_block, n = _re.subn(r'href="pesika/[^"]*"', f'href="{vault_url}"', block, count=1)
    if n == 1:
        raw = raw[:idx] + new_block + raw[end:]
        replaced += 1
    else:
        print('WARN: no pesika href in slot for', a['case'])

open(idx_path, 'w', encoding='utf-8').write(raw)
print('appendix hrefs replaced:', replaced)
