import json, re

REPO = '/Users/ohadlevy/Projects/taavoura-binder'
raw = open(REPO + '/index.html', encoding='utf-8').read()

m = re.search(r'(<script id="search-index" type="application/json">)(.*?)(</script>)', raw, re.S)
data = json.loads(m.group(2))
before = len(data)
data = [row for row in data if row['id'] != 'c-appendix']
print('search rows:', before, '->', len(data))

new_json = json.dumps(data, ensure_ascii=False)
raw2 = raw[:m.start(2)] + new_json + raw[m.end(2):]
open(REPO + '/index.html', 'w', encoding='utf-8').write(raw2)
