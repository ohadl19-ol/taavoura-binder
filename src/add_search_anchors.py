# -*- coding: utf-8 -*-
import re

REPO = '/Users/ohadlevy/Projects/taavoura-binder'
raw = open(REPO + '/index.html', encoding='utf-8').read()

def splice_ids(raw, pattern, id_prefix, insert_after):
    """For every match of `pattern`, insert an id="{prefix}-{n}" right after `insert_after`
    (a literal substring that must appear once inside each match, e.g. the class attribute)."""
    matches = list(re.finditer(pattern, raw))
    edits = []
    for i, m in enumerate(matches):
        seg = m.group(0)
        pos = seg.find(insert_after)
        assert pos != -1
        insert_at = m.start() + pos + len(insert_after)
        edits.append((insert_at, ' id="' + id_prefix + '-' + str(i) + '"'))
    for pos, text in reversed(edits):
        raw = raw[:pos] + text + raw[pos:]
    return raw, len(matches)

# 1) case-title divs -> id="case-N" (two historical formats: with or without a data-case attr)
raw, n_case = splice_ids(raw, r'<div class="case-title"(?: data-case="[^"]*")?>', 'case', 'class="case-title"')
print('case-title anchors:', n_case)

# 2) topic-title divs -> id="topic-N"
raw, n_topic = splice_ids(raw, r'<div class="topic-title">', 'topic', 'class="topic-title"')
print('topic-title anchors:', n_topic)

# 3) data rows (tr immediately followed by td, i.e. not header rows with th) -> id="row-N"
matches = list(re.finditer(r'<tr>(?=<td>)', raw))
edits = []
for i, m in enumerate(matches):
    insert_at = m.start() + len('<tr')  # right after "<tr", before the closing ">"
    edits.append((insert_at, ' id="row-' + str(i) + '"'))
for pos, text in reversed(edits):
    raw = raw[:pos] + text + raw[pos:]
n_row = len(matches)
print('table row anchors:', n_row)

open(REPO + '/index.html', 'w', encoding='utf-8').write(raw)
print('done')
