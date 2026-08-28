import os, json

CL_DIR = '/Users/ohadlevy/Library/Mobile Documents/com~apple~CloudDocs/עבודה /תעבורה/מאגר פסיקה לקלסר/פסקי דין'
matched = json.load(open('/tmp/matched.json', encoding='utf-8'))

used_local = set()
for m in matched:
    lp = m['csv']['קובץ מקומי']
    if lp:
        used_local.add(os.path.basename(lp))

# appendix items don't carry the original local path directly; recompute from unmatched csv
unmatched = json.load(open('/tmp/unmatched_csv.json', encoding='utf-8'))
for row in unmatched:
    if row['קובץ מקומי']:
        used_local.add(os.path.basename(row['קובץ מקומי']))

all_files = set(os.listdir(CL_DIR))
all_files.discard('.DS_Store')
unused = all_files - used_local
print('all files:', len(all_files))
print('used:', len(used_local))
print('unused:', unused)
