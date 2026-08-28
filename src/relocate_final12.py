# -*- coding: utf-8 -*-
import re, html as htmlmod

REPO = '/Users/ohadlevy/Projects/taavoura-binder'
raw = open(REPO + '/index.html', encoding='utf-8').read()

# case_key must match the exact data-case text currently used in the appendix
PLAN = [
    ('עפ״ת 65668-02-20', 'c16',
     'שימוש בטלפון בזמן נהיגה', 'שופט תצפית ושמשות מוכהות',
     'ניתן לבסס עבירת שימוש בטלפון על תצפית שוטר גם דרך שמשה כהה, בכפוף למהימנות התצפית; ציפוי השמשה עשוי לבסס עבירה נפרדת.'),
    ('עפ״ת 32572-02-19', 'c2', None, None,
     'אושר למעשה ברע"פ 1771/19: אין די בטענה כללית של "לא קיבלתי את הדו"ח" כדי לסתור חזקת מסירה; טענות לשיבושי דואר טעונות תימוכין ממשיים. אין די בהיעדר תצהיר התומך בבקשה להארכת מועד להישפט.'),
    ('פל״א 3230-03-25', 'c9', None, None,
     'שילוב של נהיגה בזמן פסילה ונהיגה תחת השפעת משקאות משכרים הוא "מכפיל חומרה" המצדיק מתחם שמתחיל במאסר בפועל ממש ויכול להגיע עד 24 חודשים.'),
    ('רע״פ 5166/14', 'c10', None, None,
     'בעבירת נהיגה בשכרות, "נהיגה" אינה מחייבת תנועה בפועל של הרכב. המבחן הוא שליטה אפקטיבית על אמצעי הפעולה של הרכב — היכולת לשלוט במנגנוני התפעול, הבקרה והשליטה, גם כשהרכב עומד.'),
    ('עפ״ת 52656-04-25', 'c12', None, None,
     'הוצאת רישיון נהיגה בדיעבד אינה "מרפאת" את עבירת בלתי מורשה מעולם ואינה נסיבה מיוחדת המצדיקה סטייה מפסילת המינימום; מתן משקל מכריע לכך פוגע בהרתעת הרבים.'),
    ('עפ״ת 57448-03-22', 'c12', None, None,
     'יש מקום להחמיר בענישה בעבירת בלתי מורשה מעולם, ואף ייתכן שהגיעה העת להטיל מאסר בפועל גם בעבירה ראשונה — אך ההחמרה צריכה להיעשות בהדרגה ותוך שמירה על אחידות הענישה.'),
    ('עמ״ת 43184-11-25', 'c12', None, None,
     'מעצר עד תום הליכים בעבירות תעבורה (ללא נהיגה בפסילה) הוא צעד חריג, אך רצידיביזם בנהיגה ללא רישיון, מאסר מותנה שלא הרתיע וחלופה בלתי מתאימה עשויים להצדיקו. מסמך הנחזה לרישיון בינלאומי אינו מועיל ללא הוכחת תוקפו.'),
    ('רע״פ 3104/11', 'c9', None, None,
     'נהיגה בזמן פסילה נושאת כפל חומרה — הן הסכנה לשלום הציבור והן הזלזול בצווי בית המשפט. במקרה של עבר תעבורתי מכביד (14 הרשעות, 8 מהן בנהיגה ללא רישיון) נדחתה בקשת רשות ערעור על 15 חודשי מאסר בפועל.'),
    ('פ״ל 4857-03-24', 'c14', None, None,
     'נהיגה במהירות קיצונית (169 קמ"ש בדרך עירונית שהמותר בה 80) מצדיקה ככלל מאסר בפועל, אף בדרך של עבודות שירות; בנסיבות אישיות חריגות ובהיעדר עבר ניתן למקם ברף הנמוך של המתחם.'),
    ('עפ״ת 42048-01-26', 'c14', None, None,
     'תקינות ואמינות מצלמת א3 מוכחות בתעודות עובד ציבור שלא נסתרו. בעל רכב/חברת השכרה המבקשים להסב דו"ח מהירות חייבים להציג תשתית ראייתית ממשית (תצהיר/עדות) המוכיחה מי נהג — אחרת לא נסתרת חזקת אחריות הבעלים.'),
    ('תת״ע 10896-07-10', 'c15', None, None,
     'בעבירות פקיעת רישיון נהיגה, מתחם הענישה נע ממאסר מותנה בנסיבות קלות ועד שנת מאסר כאשר מדובר בעבירות חוזרות ובעבר תעבורתי עשיר; אי-ריפוי הפגם לאורך זמן מחמיר את הענישה.'),
    ('עפ״ת 46942-02-26', 'c16', None, None,
     'תקופת ההתיישנות המקוצרת (4 חודשים) חלה רק כאשר החשד מבוסס על צילום רכב בלבד. כאשר שוטר ראה את העבירה, ערך דו"ח פעולה וצילם במצלמה ידנית — חלה תקופת ההתיישנות הרגילה של שנה. די במשלוח ההודעה בדואר רשום במועד; תקלת דואר אינה מקימה התיישנות.'),
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

def rebuild_block(block, new_desc):
    """Replace the <p>...</p> inside the block (between case-title close and case-link-slot open) with new_desc."""
    title_end = block.find('</div>') + len('</div>')
    slot_start = block.find('<div class="case-link-slot"')
    title_part = block[:title_end]
    slot_part = block[slot_start:]
    return title_part + '<p>' + htmlmod.escape(new_desc) + '</p>' + slot_part

def insert_at_chapter_end(raw, chapter_id, insert_html):
    # find this chapter's <div class="chapter-body"> ... </div></section> boundary by scanning
    start = raw.find('id="' + chapter_id + '"')
    assert start != -1, chapter_id
    section_end = raw.find('</section>', start)
    assert section_end != -1
    # walk backward from section_end to the matching chapter-body close (last </div> before </section>)
    close = raw.rfind('</div>', start, section_end)
    return raw[:close] + insert_html + raw[close:]

by_chapter = {}
for case_key, chapter_id, group_label, group_note, desc in PLAN:
    raw, block = extract_block(raw, case_key)
    assert block, 'not found: ' + case_key
    block = rebuild_block(block, desc)
    by_chapter.setdefault(chapter_id, []).append(block)

for chapter_id, blocks in by_chapter.items():
    html = '<div class="topic-title"><strong>פסיקה נוספת</strong></div>' + ''.join(blocks)
    raw = insert_at_chapter_end(raw, chapter_id, html)

open(REPO + '/index.html', 'w', encoding='utf-8').write(raw)
print('relocated', len(PLAN), 'cases across', len(by_chapter), 'chapters:', list(by_chapter.keys()))
