import re

REPO = '/Users/ohadlevy/Projects/taavoura-binder'
raw = open(REPO + '/index.html', encoding='utf-8').read()

start = raw.find('<div class="chapter" id="c-appendix"')
assert start != -1
end = raw.find('</div>', raw.find('<div class="chapter-body">', start))
# chapter-body closes right after the intro <p>; then the chapter div itself closes
# safer: find matching closing by scanning to the next top-level '<div class="chapter"' or end marker
next_marker = '<div class="progress-bar" id="progress-bar">'
end2 = raw.find(next_marker)
assert end2 != -1 and end2 > start

removed = raw[start:end2]
print('removing', len(removed), 'chars')
raw2 = raw[:start] + raw[end2:]

nav_pattern = re.compile(r'<li><a class="nav-link" data-target="c-appendix"[^<]*<[^<]*<[^<]*</a></li>')
raw3, n = nav_pattern.subn('', raw2)
print('nav entries removed:', n)

open(REPO + '/index.html', 'w', encoding='utf-8').write(raw3)
