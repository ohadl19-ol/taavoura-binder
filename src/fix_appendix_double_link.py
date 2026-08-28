import re

REPO = '/Users/ohadlevy/Projects/taavoura-binder'
raw = open(REPO + '/index.html', encoding='utf-8').read()

pattern = re.compile(
    r'(<div class="case-title" data-case="([^"]*)"><strong>)'
    r'<a class="inline-case-link" href="[^"]*"[^>]*>(.*?)</a>'
    r'(</strong></div>)',
    re.S
)

count = 0
def repl(m):
    global count
    count += 1
    return m.group(1) + m.group(3) + m.group(4)

raw2 = pattern.sub(repl, raw)
print('unwrapped:', count)
open(REPO + '/index.html', 'w', encoding='utf-8').write(raw2)
