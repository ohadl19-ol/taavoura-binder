# -*- coding: utf-8 -*-
import json, re

REPO = '/Users/ohadlevy/Projects/taavoura-binder'

# ---- 1) links.json: strip any Notion urls; merge in the appendix's vault links ----
links = json.load(open(REPO + '/links.json', encoding='utf-8'))
cleared = 0
for k, v in list(links.items()):
    if v and 'app.notion.com' in v:
        links[k] = ''
        cleared += 1
print('notion values cleared in links.json:', cleared)

appendix = json.load(open('/tmp/appendix.json', encoding='utf-8'))
vault_ids = json.load(open('/tmp/vault_ids.json', encoding='utf-8'))
added = 0
for a in appendix:
    key = 'APPX::' + a['case']
    if key in vault_ids and a['case'] not in links:
        links[a['case']] = 'https://psika-north.vercel.app/files/' + vault_ids[key]['id']
        added += 1
print('appendix entries merged into links.json:', added)

json.dump(links, open(REPO + '/links.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---- 2) index.html: strip every baked <a class="chip"> inside every .case-link-slot ----
raw = open(REPO + '/index.html', encoding='utf-8').read()

def strip_chips(html_text):
    def repl(m):
        return m.group(1) + m.group(3)
    # match: <div class="case-link-slot" data-case="...">  ...chips...  </div>
    pattern = re.compile(
        r'(<div class="case-link-slot"[^>]*>)(.*?)(</div>)', re.S
    )
    return pattern.sub(lambda m: m.group(1) + m.group(3), html_text)

before = len(re.findall(r'<div class="case-link-slot"[^>]*>.*?</div>', raw))
raw2 = strip_chips(raw)
after_chips = raw2.count('<a class="chip"')
open(REPO + '/index.html', 'w', encoding='utf-8').write(raw2)
print('case-link-slots processed:', before)
print('remaining baked chips anywhere in file:', after_chips)
