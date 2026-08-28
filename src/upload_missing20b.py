# -*- coding: utf-8 -*-
import json, os
from upload_to_vault import fetch_existing, upload_file, insert_record, normalize_case_number

src = '/tmp/missing20_pdf/פל 1460-10-13 מדינת ישראל נ הוד אילן שכטר.pdf'
key = 'פ״ל (תעבורה פתח תקווה) 1460-10-13 מדינת ישראל נ׳ הוד אילן שכטר'

existing = fetch_existing()
existing_by_norm = {e['normalized_case_number']: e for e in existing}
norm = normalize_case_number(key)

results = json.load(open('/tmp/missing20_ids.json', encoding='utf-8'))

if norm in existing_by_norm:
    results[key] = existing_by_norm[norm]['id']
    print('reused')
else:
    storage_path, file_hash, size = upload_file(src, 'pdf', 'application/pdf')
    new_id = insert_record(
        title=key, case_number=key, storage_path=storage_path,
        original_filename=os.path.basename(src), mime='application/pdf',
        size=size, file_hash=file_hash,
    )
    results[key] = new_id
    print('uploaded', new_id)

json.dump(results, open('/tmp/missing20_ids.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('total results:', len(results))
