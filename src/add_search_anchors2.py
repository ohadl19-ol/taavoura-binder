# -*- coding: utf-8 -*-
import re

REPO = '/Users/ohadlevy/Projects/taavoura-binder'
raw = open(REPO + '/index.html', encoding='utf-8').read()

def max_index(raw, prefix):
    nums = [int(m) for m in re.findall(r'id="' + prefix + r'-(\d+)"', raw)]
    return max(nums) if nums else -1

def splice_ids(raw, pattern, id_prefix, insert_after, start):
    matches = list(re.finditer(pattern, raw))
    edits = []
    for i, m in enumerate(matches):
        seg = m.group(0)
        pos = seg.find(insert_after)
        assert pos != -1
        insert_at = m.start() + pos + len(insert_after)
        edits.append((insert_at, ' id="' + id_prefix + '-' + str(start + i) + '"'))
    for pos, text in reversed(edits):
        raw = raw[:pos] + text + raw[pos:]
    return raw, len(matches)

start_topic = max_index(raw, 'topic') + 1
raw, n_topic = splice_ids(raw, r'<div class="topic-title">', 'topic', 'class="topic-title"', start_topic)
print('new topic-title anchors:', n_topic, 'starting at', start_topic)

start_row = max_index(raw, 'row') + 1
matches = list(re.finditer(r'<tr>(?=<td>)', raw))
edits = []
for i, m in enumerate(matches):
    insert_at = m.start() + len('<tr')
    edits.append((insert_at, ' id="row-' + str(start_row + i) + '"'))
for pos, text in reversed(edits):
    raw = raw[:pos] + text + raw[pos:]
print('new row anchors:', len(matches), 'starting at', start_row)

open(REPO + '/index.html', 'w', encoding='utf-8').write(raw)
print('done')
