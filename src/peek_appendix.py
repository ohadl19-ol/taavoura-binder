import json
a = json.load(open('/tmp/appendix.json', encoding='utf-8'))
print(len(a))
for x in a[:5]:
    print(x['case'], '|', x['href'])
    print(' ', x['desc'][:150])
