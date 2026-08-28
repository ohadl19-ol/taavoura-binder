import json
unmatched = json.load(open('/tmp/unmatched_csv.json', encoding='utf-8'))
appendix = []
for row in unmatched:
    if row['קובץ מקומי']:
        appendix.append({'case': row['הליך'], 'desc': row['תיאור'], 'local': row['קובץ מקומי']})
json.dump(appendix, open('/tmp/appendix.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(appendix))
