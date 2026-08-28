# -*- coding: utf-8 -*-
import json, html as htmlmod, re, os

REPO = '/Users/ohadlevy/Projects/taavoura-binder'
idx_path = os.path.join(REPO, 'index.html')
raw = open(idx_path, encoding='utf-8').read()

appendix = json.load(open('/tmp/appendix.json', encoding='utf-8'))
print('appendix entries:', len(appendix))

CH_ID = 'c-appendix'

parts = []
parts.append('<div class="chapter" id="' + CH_ID + '" data-num="נספח">')
parts.append('<div class="chapter-head"><span class="chapter-num">נספח</span><h2 class="chapter-title">פסיקה נוספת מהמאגר המקומי</h2></div>')
parts.append('<div class="chapter-body">')
parts.append('<p>פסקי דין נוספים שאותרו והורדו למאגר הפסיקה המקומי, ועדיין אינם משובצים תחת נושא ספציפי בקלסר. הקישורים פותחים את הקובץ המקומי, ללא תלות בנבו או בהתחברות.</p>')
for item in appendix:
    case = htmlmod.escape(item['case'])
    desc = htmlmod.escape(item['desc'])
    href = htmlmod.escape(item['href'])
    data_case = htmlmod.escape(item['case'], quote=True)
    parts.append('<div class="case-title" data-case="' + data_case + '"><strong>' + case + '</strong></div>')
    parts.append('<p>' + desc + '</p>')
    parts.append('<div class="case-link-slot" data-case="' + data_case + '"><a class="chip" href="' + href + '" target="_blank" rel="noopener">📄 פסק הדין המלא</a></div>')
parts.append('</div>')
parts.append('</div>')
chapter_html = ''.join(parts)

marker = '<button class="to-top"'
n = raw.count(marker)
print('marker occurrences:', n)
assert n == 1
raw2 = raw.replace(marker, chapter_html + '\n' + marker, 1)

nav_entry = (
    '<li><a class="nav-link" data-target="' + CH_ID + '" href="#' + CH_ID + '">'
    '<span class="nav-num">נספח</span><span>פסיקה נוספת</span></a></li>'
)
nav_close = raw2.rfind('</nav>')
ul_close = raw2.rfind('</ul>', 0, nav_close)
print('ul_close pos:', ul_close)
assert ul_close != -1
raw2 = raw2[:ul_close] + nav_entry + raw2[ul_close:]

m = re.search(r'(<script id="search-index" type="application/json">)(.*?)(</script>)', raw2, re.S)
assert m
search_json = json.loads(m.group(2))
label = 'פסיקה נוספת'
text = ' '.join(item['case'] + ' ' + item['desc'] for item in appendix)
search_json.append({'id': CH_ID, 'label': label, 'text': text})
new_search = json.dumps(search_json, ensure_ascii=False)
raw2 = raw2[:m.start(2)] + new_search + raw2[m.end(2):]

open(idx_path, 'w', encoding='utf-8').write(raw2)
print('index.html updated, new size:', len(raw2))
