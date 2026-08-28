from bs4 import BeautifulSoup
raw = open('/Users/ohadlevy/Projects/taavoura-binder/index.html', encoding='utf-8').read()
soup = BeautifulSoup(raw, 'lxml')
print('chapters:', len(soup.select('.chapter')))
ch = soup.select_one('#c-sentencing')
print('sentencing chapter found:', ch is not None)
if ch:
    print('tables in it:', len(ch.select('table')))
    print('rows total:', len(ch.select('tbody tr')))
main = soup.select_one('main.main .content')
print('sentencing chapter inside .content:', ch in (main.select('.chapter') if main else []))
print('nav entry:', soup.select_one('a[data-target="c-sentencing"]') is not None)
print('case-link-slot count (should be unchanged, 91):', len(soup.select('.case-link-slot')))
print('scripts:', len(soup.find_all('script')))
