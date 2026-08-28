import json
matched = json.load(open('/tmp/matched.json', encoding='utf-8'))
links = json.load(open('/Users/ohadlevy/Projects/taavoura-binder/links.json', encoding='utf-8'))
for m in matched:
    if not links[m['full_key']].startswith('pesika/'):
        print(m['full_key'], '|', m['csv']['קובץ מקומי'], '|', m['csv']['סטטוס'])
