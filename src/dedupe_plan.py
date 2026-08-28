import json
from collections import Counter
plan = json.load(open('/tmp/replace_plan.json', encoding='utf-8'))
ids = Counter(p['id'] for p in plan)
dupes = {k: v for k, v in ids.items() if v > 1}
print('duplicate id targets:', dupes)
for p in plan:
    if p['id'] in dupes:
        print(' ', p['file'], '->', p['id'])
