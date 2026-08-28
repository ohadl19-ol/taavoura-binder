# -*- coding: utf-8 -*-
import json
from upload_to_vault import fetch_existing, upload_file, insert_record, normalize_case_number

plan = json.load(open('/tmp/upload_plan.json', encoding='utf-8'))
existing = fetch_existing()
existing_by_norm = {}
for e in existing:
    existing_by_norm.setdefault(e['normalized_case_number'], e)

results = {}
reused = 0
uploaded = 0
errors = []

for it in plan:
    norm = normalize_case_number(it['case_number'])
    if norm in existing_by_norm:
        results[it['key']] = {'id': existing_by_norm[norm]['id'], 'reused': True}
        reused += 1
        continue
    try:
        storage_path, file_hash, size = upload_file(it['local_src'], it['ext'], it['mime'])
        new_id = insert_record(
            title=it['title'],
            case_number=it['case_number'],
            storage_path=storage_path,
            original_filename=it['orig_filename'],
            mime=it['mime'],
            size=size,
            file_hash=file_hash,
        )
        results[it['key']] = {'id': new_id, 'reused': False}
        existing_by_norm[norm] = {'id': new_id}  # avoid re-uploading dup within this same run
        uploaded += 1
    except Exception as ex:
        errors.append({'key': it['key'], 'error': str(ex)})

print('uploaded new:', uploaded)
print('reused existing:', reused)
print('errors:', len(errors))
for e in errors:
    print(' ERROR:', e['key'], '|', e['error'][:200])

json.dump(results, open('/tmp/vault_ids.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(errors, open('/tmp/vault_errors.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
