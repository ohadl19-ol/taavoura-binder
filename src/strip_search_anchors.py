import re
REPO = '/Users/ohadlevy/Projects/taavoura-binder'
raw = open(REPO + '/index.html', encoding='utf-8').read()

before = len(re.findall(r' id="(?:case|topic|row)-\d+"', raw))
raw2 = re.sub(r' id="(?:case|topic|row)-\d+"', '', raw)
after = len(re.findall(r' id="(?:case|topic|row)-\d+"', raw2))
print('stripped:', before, '-> remaining:', after)
open(REPO + '/index.html', 'w', encoding='utf-8').write(raw2)
