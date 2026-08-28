import json, re
from bs4 import BeautifulSoup

REPO = '/Users/ohadlevy/Projects/taavoura-binder'
raw = open(REPO + '/index.html', encoding='utf-8').read()
soup = BeautifulSoup(raw, 'lxml')

m = re.search(r'(<script id="search-index" type="application/json">)(.*?)(</script>)', raw, re.S)
search_json = json.loads(m.group(2))

for row in search_json:
    el = soup.select_one('#' + row['id'])
    if el:
        row['text'] = re.sub(r'\s+', ' ', el.get_text(' ', strip=True)).strip()

new_search = json.dumps(search_json, ensure_ascii=False)
raw2 = raw[:m.start(2)] + new_search + raw[m.end(2):]
open(REPO + '/index.html', 'w', encoding='utf-8').write(raw2)
print('search index refreshed for', len(search_json), 'entries')
