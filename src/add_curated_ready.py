# -*- coding: utf-8 -*-
import json, re, html as htmlmod

REPO = '/Users/ohadlevy/Projects/taavoura-binder'
raw = open(REPO + '/index.html', encoding='utf-8').read()
links = json.load(open(REPO + '/links.json', encoding='utf-8'))

VAULT_BASE = 'https://psika-north.vercel.app/files/'

PLAN = [
    ('עפ״ת 76760-03-25', 'c18',
     '9ef79a59-aca7-4efb-a5cb-e2aeea7af91d',
     'ערעור המדינה על קולת העונש בגין נהיגה בקלות ראש וסטייה מנתיב שגרמה לחבלה של ממש (קטיעת אצבע) התקבל: בשל רשלנות בינונית-גבוהה הוחמר המאסר מ‑6 ל‑9 חודשי עבודות שירות.'),
    ('עפ״ת (באר שבע) 31900-01-25', 'c13',
     '14fc3098-87f5-4de1-ab6b-74d3051bec00',
     '״עונש המינימום כשמו כן הוא״ — ערעור התביעה על אי-הטלת פסילת מינימום בעבירת בלתי מורשה לסוג התקבל; מעבר מבחני הרישוי בדיעבד, לאחר ביצוע העבירה, אינו מצדיק חריגה מפסילת המינימום.'),
    ('ע״ח 31129-08-19', 'c4',
     'f388eaad-b527-4f59-97f0-9b603a942ac4',
     'על בעל רכב חלה חובה מוגברת לברר לפני מסירת הרכב אם הנהג שתה ולוודא את כשירותו לנהיגה; היכרות אישית עם הנהג או התרשמות חיצונית שאינו שיכור אינן מספיקות, במיוחד כשבעל הרכב אוסף אותו ממסיבת לילה.'),
    ('עמ״ת 43405-11-25', 'c7',
     'f531b84b-c39b-4be9-ac70-b5dc3d9bad67',
     'עורר שיצא מחלון יציאה שאושר לצורך טיפול רפואי ולא הגיע כלל למרפאה, ובחקירתו מסר גרסה כוזבת — חוסר האמינות שולל אפשרות להסתמך עליו בחלופת מעצר או באיזוק אלקטרוני; הערר נדחה והמעצר עד תום ההליכים נותר על כנו.'),
]

def insert_at_chapter_end(raw, chapter_id, insert_html):
    start = raw.find('id="' + chapter_id + '"')
    assert start != -1, chapter_id
    section_end = raw.find('</section>', start)
    assert section_end != -1
    close = raw.rfind('</div>', start, section_end)
    return raw[:close] + insert_html + raw[close:]

by_chapter = {}
for case_key, chapter_id, vault_id, desc in PLAN:
    by_chapter.setdefault(chapter_id, []).append((case_key, vault_id, desc))

for chapter_id, items in by_chapter.items():
    parts = ['<div class="topic-title"><strong>פסיקה נוספת</strong></div>']
    for case_key, vault_id, desc in items:
        data_case = htmlmod.escape(case_key, quote=True)
        parts.append('<div class="case-title" data-case="' + data_case + '"><strong>' + htmlmod.escape(case_key) + '</strong></div>')
        parts.append('<p>' + htmlmod.escape(desc) + '</p>')
        parts.append('<div class="case-link-slot" data-case="' + data_case + '"></div>')
        links[case_key] = VAULT_BASE + vault_id
    raw = insert_at_chapter_end(raw, chapter_id, ''.join(parts))

open(REPO + '/index.html', 'w', encoding='utf-8').write(raw)
json.dump(links, open(REPO + '/links.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('added', len(PLAN), 'cases across', len(by_chapter), 'chapters:', list(by_chapter.keys()))
