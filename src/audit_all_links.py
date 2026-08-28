import re, json
REPO = '/Users/ohadlevy/Projects/taavoura-binder'
raw = open(REPO + '/index.html', encoding='utf-8').read()

A_RE = re.compile(r'<a\s+[^>]*?href="([^"]*)"[^>]*>(.*?)</a>', re.S)
non_vault = []
for m in A_RE.finditer(raw):
    href, inner = m.group(1), m.group(2)
    if 'psika-north.vercel.app' in href:
        continue
    plain = re.sub(r'<[^>]+>', ' ', inner).strip()
    non_vault.append((href, plain))

print('total non-vault <a> tags:', len(non_vault))
for href, text in non_vault:
    print(' ', text[:60], '|', href[:80])
