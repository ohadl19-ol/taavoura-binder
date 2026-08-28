# -*- coding: utf-8 -*-
import json, os, re, shutil, html as htmlmod

REPO = '/Users/ohadlevy/Projects/taavoura-binder'
CL_DIR = '/Users/ohadlevy/Library/Mobile Documents/com~apple~CloudDocs/עבודה /תעבורה/מאגר פסיקה לקלסר'
OUT = os.path.join(REPO, 'pesika')
os.makedirs(OUT, exist_ok=True)

TXT_TEMPLATE = """<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Frank+Ruhl+Libre:wght@400;700&family=Assistant:wght@400;600&display=swap" rel="stylesheet">
<style>
  :root{{ --paper:#f6f1e6; --surface:#fffdf9; --ink:#241f19; --ink-soft:#5f5646; --line:#e0d5bd; --navy:#1d3350; }}
  @media (prefers-color-scheme: dark){{
    :root{{ --paper:#15171c; --surface:#1c1f26; --ink:#ece6d8; --ink-soft:#b3ab98; --line:#343b48; --navy:#8fb4e0; }}
  }}
  body{{ margin:0; background:var(--paper); color:var(--ink); font-family:"Assistant",sans-serif; line-height:1.85; }}
  .wrap{{ max-width:800px; margin:0 auto; padding:36px 24px 100px; }}
  header{{ margin-bottom:28px; border-bottom:1px solid var(--line); padding-bottom:16px; }}
  header a{{ font-size:13px; color:var(--navy); text-decoration:none; }}
  h1{{ font-family:"Frank Ruhl Libre",serif; font-size:22px; margin:10px 0 0; }}
  pre{{ white-space:pre-wrap; word-break:break-word; font-family:"Assistant",sans-serif; font-size:15.5px; background:var(--surface); border:1px solid var(--line); border-radius:10px; padding:22px 24px; }}
</style>
</head>
<body>
<div class="wrap">
<header><a href="javascript:history.back()">&#8594; חזרה לקלסר</a><h1>{title}</h1></header>
<pre>{body}</pre>
</div>
</body>
</html>
"""

def slugify(name):
    name = name.strip()
    name = re.sub(r'\s+', '-', name)
    return name

def copy_case_file(rel_local_path, case_label):
    """rel_local_path like 'פסקי דין/רעפ 8427-17.txt' -> returns relative href under /pesika/."""
    src = os.path.join(CL_DIR, rel_local_path)
    if not os.path.isfile(src):
        return None
    base = os.path.basename(rel_local_path)
    stem, ext = os.path.splitext(base)
    ext = ext.lower()
    safe_stem = slugify(stem)
    if ext == '.txt':
        text = open(src, encoding='utf-8', errors='replace').read()
        out_name = safe_stem + '.html'
        out_path = os.path.join(OUT, out_name)
        page = TXT_TEMPLATE.format(title=htmlmod.escape(case_label), body=htmlmod.escape(text))
        open(out_path, 'w', encoding='utf-8').write(page)
        return 'pesika/' + out_name
    else:
        out_name = safe_stem + ext
        out_path = os.path.join(OUT, out_name)
        shutil.copyfile(src, out_path)
        return 'pesika/' + out_name

# ---- part A: update links.json for the 54 matches to existing binder citations ----
links = json.load(open(os.path.join(REPO, 'links.json'), encoding='utf-8'))
matched = json.load(open('/tmp/matched.json', encoding='utf-8'))

updated = 0
for m in matched:
    row = m['csv']
    if not row['קובץ מקומי']:
        continue
    href = copy_case_file(row['קובץ מקומי'], m['full_key'])
    if href:
        links[m['full_key']] = href
        updated += 1

json.dump(links, open(os.path.join(REPO, 'links.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('links.json updated:', updated, 'of', len(matched), 'matches')

# ---- part B: build appendix data for the unmatched (new) CSV entries ----
unmatched = json.load(open('/tmp/unmatched_csv.json', encoding='utf-8'))
appendix = []
for row in unmatched:
    if not row['קובץ מקומי']:
        continue
    href = copy_case_file(row['קובץ מקומי'], row['הליך'])
    if href:
        appendix.append({
            'case': row['הליך'],
            'desc': row['תיאור'],
            'href': href,
        })

json.dump(appendix, open('/tmp/appendix.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('appendix entries with hosted files:', len(appendix))

print('pesika files written:', len(os.listdir(OUT)))
