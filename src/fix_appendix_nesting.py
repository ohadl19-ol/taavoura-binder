# -*- coding: utf-8 -*-
REPO = '/Users/ohadlevy/Projects/taavoura-binder'
raw = open(REPO + '/index.html', encoding='utf-8').read()

start_marker = '<div class="chapter" id="c-appendix" data-num="נספח">'
start = raw.find(start_marker)
assert start != -1

end_marker = '<div class="progress-bar" id="progress-bar"></div>'
end = raw.find(end_marker)
assert end != -1
assert end > start

appendix_html = raw[start:end]
print('appendix block length:', len(appendix_html))

# remove it from its current (wrong, out-of-.content) position
without_appendix = raw[:start] + raw[end:]

# re-insert right before the "</div>\n  </main>\n</div>" close sequence
close_marker = '    </div>\n  </main>\n</div>'
idx = without_appendix.find(close_marker)
assert idx != -1, 'close marker not found'

fixed = without_appendix[:idx] + appendix_html + without_appendix[idx:]
open(REPO + '/index.html', 'w', encoding='utf-8').write(fixed)
print('fixed. new size:', len(fixed))
