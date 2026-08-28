# -*- coding: utf-8 -*-
import json

REPO = '/Users/ohadlevy/Projects/taavoura-binder'
KEY = 'ע״פ (מחוזי באר שבע) 4357/07 לאון נ׳ מדינת ישראל'

raw = open(REPO + '/index.html', encoding='utf-8').read()

start_marker = '<div class="case-title"><strong>' + KEY + '</strong></div>'
start = raw.find(start_marker)
assert start != -1, 'case-title block not found'

end_marker = '<div class="topic-title"><strong>מהירות קצה'
end = raw.find(end_marker, start)
assert end != -1, 'end marker not found'

removed = raw[start:end]
print('removing', len(removed), 'chars')
print('--- preview ---')
print(removed[:400])

raw2 = raw[:start] + raw[end:]
open(REPO + '/index.html', 'w', encoding='utf-8').write(raw2)

links = json.load(open(REPO + '/links.json', encoding='utf-8'))
if KEY in links:
    del links[KEY]
    print('removed from links.json')
json.dump(links, open(REPO + '/links.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('links.json entries now:', len(links))
