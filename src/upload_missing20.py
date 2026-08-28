# -*- coding: utf-8 -*-
import json, os
from upload_to_vault import fetch_existing, upload_file, insert_record, normalize_case_number

FOLDER = '/Users/ohadlevy/Library/Mobile Documents/com~apple~CloudDocs/עבודה /תעבורה/מאגר פסיקה לקלסר/20 פסקי דין מקוריים שחסרו'
matches = json.load(open('/tmp/missing20_matches.json', encoding='utf-8'))

def resolve(fname):
    if fname.endswith('.doc'):
        return os.path.join(FOLDER, fname), 'doc', 'application/msword', fname
    if fname.endswith('.html'):
        stem = os.path.splitext(fname)[0]
        return f'/tmp/missing20_pdf/{stem}.pdf', 'pdf', 'application/pdf', stem + '.pdf'
    return None, None, None, None

existing = fetch_existing()
existing_by_norm = {e['normalized_case_number']: e for e in existing}

results = {}
uploaded = 0
reused = 0
errors = []

for m in matches:
    src, ext, mime, orig = resolve(m['file'])
    if not src or not os.path.isfile(src):
        errors.append({'key': m['full_key'], 'error': 'local file missing: ' + str(src)})
        continue
    norm = normalize_case_number(m['full_key'])
    if norm in existing_by_norm:
        results[m['full_key']] = existing_by_norm[norm]['id']
        reused += 1
        continue
    try:
        storage_path, file_hash, size = upload_file(src, ext, mime)
        new_id = insert_record(
            title=m['full_key'], case_number=m['full_key'],
            storage_path=storage_path, original_filename=orig,
            mime=mime, size=size, file_hash=file_hash,
        )
        results[m['full_key']] = new_id
        existing_by_norm[norm] = {'id': new_id}
        uploaded += 1
    except Exception as ex:
        errors.append({'key': m['full_key'], 'error': str(ex)})

print('uploaded:', uploaded, '| reused:', reused, '| errors:', len(errors))
for e in errors:
    print('ERROR:', e)

json.dump(results, open('/tmp/missing20_ids.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
