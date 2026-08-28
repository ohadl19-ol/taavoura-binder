import json, re

REPO = '/Users/ohadlevy/Projects/taavoura-binder'
raw = open(REPO + '/index.html', encoding='utf-8').read()

m = re.search(r'(<script id="search-index" type="application/json">)(.*?)(</script>)', raw, re.S)
data = json.loads(m.group(2))

snippet = 'ע״פ (מחוזי באר שבע) 4357/07 לאון נ׳ מדינת ישראל ביחס לנהיגה במהירות של 160 קמ״ש במקום 90 קמ״ש נקבע: “ראוי לסווג נהיגה במהירות של 160 קמ״ש, דהיינו 70 קמ״ש מעל המותר, כ׳טיסה׳.” נקבע כי מהירות כזו מצמצמת באופן משמעותי את יכולת התגובה והתמרון ומעמידה בסיכון ממשי את יתר המשתמשים בדרך. הציטוט מתאים לטיעון לעונש גם כאשר המהירות אינה מגיעה לרף של מהירות קצה. '

found = False
for row in data:
    if 'לאון' in row.get('text', ''):
        before = row['text']
        row['text'] = row['text'].replace(' 160 קמ״ש במקום 90 ' + snippet, ' ').replace(snippet, '')
        row['text'] = re.sub(r'\s+', ' ', row['text']).strip()
        found = True
        print('cleaned id:', row['id'])

print('found:', found)
new_json = json.dumps(data, ensure_ascii=False)
raw2 = raw[:m.start(2)] + new_json + raw[m.end(2):]
open(REPO + '/index.html', 'w', encoding='utf-8').write(raw2)
