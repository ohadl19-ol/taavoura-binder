# -*- coding: utf-8 -*-
import re, json, html as htmlmod

REPO = '/Users/ohadlevy/Projects/taavoura-binder'
raw = open(REPO + '/index.html', encoding='utf-8').read()

TO_MESH = [  # -> chapter c2 (המ"ש)
    'רע״פ 8427/17', 'רע״פ 6153/20', 'רע״פ 1771/19', 'רע״פ 2600/22', 'רע״פ 394/22',
    'עפ״ת 59787-01-25', 'עפ״ת 20173-06-23', 'עפ״ת 60802-12-22', 'רע״פ 4849/24',
]
TO_PSILA = [  # -> chapter c9 (נהיגה בזמן פסילה)
    'רע״פ 1211/12', 'תתע״א 2916-10-23', 'תת״ע 4701-09-24',
]

def extract_block(raw, case_key):
    marker = '<div class="case-title" data-case="' + htmlmod.escape(case_key, quote=True) + '">'
    start = raw.find(marker)
    if start == -1:
        return raw, None
    slot_marker = '<div class="case-link-slot" data-case="' + htmlmod.escape(case_key, quote=True) + '">'
    slot_start = raw.find(slot_marker, start)
    assert slot_start != -1, case_key
    slot_end = raw.find('</div>', slot_start) + len('</div>')
    block = raw[start:slot_end]
    raw2 = raw[:start] + raw[slot_end:]
    return raw2, block

mesh_blocks = []
for k in TO_MESH:
    raw, b = extract_block(raw, k)
    assert b, 'not found: ' + k
    mesh_blocks.append(b)

psila_blocks = []
for k in TO_PSILA:
    raw, b = extract_block(raw, k)
    assert b, 'not found: ' + k
    psila_blocks.append(b)

def insert_before_chapter_close(raw, next_chapter_id, insert_html):
    pattern = re.compile(r'(</div>)(\s*</section>\s*<section class="chapter" id="' + next_chapter_id + r'")')
    m = pattern.search(raw)
    assert m, 'insertion point not found for ' + next_chapter_id
    return raw[:m.start(1)] + insert_html + raw[m.start(1):]

mesh_html = '<div class="topic-title"><strong>פסיקה נוספת — חזקת מסירה והארכת מועד</strong></div>' + ''.join(mesh_blocks)
raw = insert_before_chapter_close(raw, 'c3', mesh_html)

psila_html = '<div class="topic-title"><strong>פסיקה נוספת</strong></div>' + ''.join(psila_blocks)
raw = insert_before_chapter_close(raw, 'c10', psila_html)

open(REPO + '/index.html', 'w', encoding='utf-8').write(raw)
print('moved', len(mesh_blocks), 'to c2,', len(psila_blocks), 'to c9')
