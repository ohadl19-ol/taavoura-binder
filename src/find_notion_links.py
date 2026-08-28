from bs4 import BeautifulSoup
raw = open('/Users/ohadlevy/Projects/taavoura-binder/index.html', encoding='utf-8').read()
soup = BeautifulSoup(raw, 'lxml')
slots = soup.select('.case-link-slot, .link-row')
count = 0
for slot in slots:
    notion_links = [a for a in slot.select('a.chip') if 'app.notion.com' in (a.get('href') or '')]
    other_links = [a for a in slot.select('a.chip') if 'app.notion.com' not in (a.get('href') or '')]
    if notion_links:
        count += 1
        case = slot.get('data-case') or '(no data-case)'
        print(case[:70], '| notion chips:', len(notion_links), '| other chips:', len(other_links))
print('total slots with a notion chip:', count)
