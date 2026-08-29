# -*- coding: utf-8 -*-
import sys

REPO = '/Users/ohadlevy/Projects/taavoura-binder'
FILES = [REPO + '/src/page_template.html', REPO + '/index.html']

EDITS = []

# 1) CSS: switch from absolute (clipped by the fixed-height sidebar) to fixed positioning
EDITS.append((
    '  .search-results{\n'
    '    display:none; position:absolute; top:100%; inset-inline:0; margin-top:6px;\n'
    '    background:var(--surface); border:1px solid var(--line-strong); border-radius:10px;\n'
    '    box-shadow:var(--shadow); max-height:60vh; overflow-y:auto; z-index:25;\n'
    '  }',
    '  .search-results{\n'
    '    display:none; position:fixed; margin-top:6px;\n'
    '    background:var(--surface); border:1px solid var(--line-strong); border-radius:10px;\n'
    '    box-shadow:var(--shadow); overflow-y:auto; z-index:25;\n'
    '  }'
))

# 2) JS: position the panel (fixed, computed from the input's own coordinates) whenever it is shown
OLD = "    resultsEl.classList.add('show');\n    return scored.length;"
NEW = (
    "    positionResults();\n"
    "    resultsEl.classList.add('show');\n"
    "    return scored.length;"
)
EDITS.append((OLD, NEW))

OLD2 = "  function normalize(s){ return (s||'').toLowerCase(); }"
NEW2 = (
    "  function normalize(s){ return (s||'').toLowerCase(); }\n\n"
    "  function positionResults(){\n"
    "    var r = input.getBoundingClientRect();\n"
    "    resultsEl.style.insetInlineStart = r.left + 'px';\n"
    "    resultsEl.style.top = (r.bottom + 6) + 'px';\n"
    "    resultsEl.style.width = r.width + 'px';\n"
    "    resultsEl.style.maxHeight = Math.max(120, window.innerHeight - r.bottom - 16) + 'px';\n"
    "  }\n"
    "  window.addEventListener('resize', function(){ if(resultsEl.classList.contains('show')) positionResults(); });"
)
EDITS.append((OLD2, NEW2))

for path in FILES:
    src = open(path, encoding='utf-8').read()
    for old, new in EDITS:
        cnt = src.count(old)
        if cnt != 1:
            print('WARN: %r... occurs %d times in %s' % (old[:50], cnt, path), file=sys.stderr)
            continue
        src = src.replace(old, new, 1)
    open(path, 'w', encoding='utf-8').write(src)
    print('patched', path)
