import json
links = json.load(open('/Users/ohadlevy/Projects/taavoura-binder/links.json', encoding='utf-8'))
for k in links:
    if k.startswith('בש״פ 7031') or k.startswith('רע״פ 4345') or k.startswith('תת״ע 1773'):
        print(repr(k), '->', links[k])
