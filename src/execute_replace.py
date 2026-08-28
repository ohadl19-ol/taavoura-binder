# -*- coding: utf-8 -*-
import json, os, hashlib, uuid, requests
from replace_with_pdfs import SUPABASE_URL, SERVICE_KEY, BUCKET, REST_HEADERS, PDF_DIR, fetch_existing

plan = json.load(open('/tmp/replace_plan.json', encoding='utf-8'))

# dedupe: keep first occurrence per id
seen_ids = set()
deduped = []
for p in plan:
    if p['id'] in seen_ids:
        continue
    seen_ids.add(p['id'])
    deduped.append(p)
print('replacing', len(deduped), 'unique files (of', len(plan), 'matches)')

existing = {e['id']: e for e in fetch_existing()}

ok = 0
errors = []
for p in deduped:
    file_id = p['id']
    row = existing.get(file_id)
    if not row:
        errors.append({'id': file_id, 'error': 'row not found in DB'})
        continue
    local_path = os.path.join(PDF_DIR, p['file'])
    data = open(local_path, 'rb').read()
    file_hash = hashlib.sha256(data).hexdigest()
    new_storage_path = f'{uuid.uuid4()}.pdf'

    up = requests.post(
        f'{SUPABASE_URL}/storage/v1/object/{BUCKET}/{new_storage_path}',
        headers={'apikey': SERVICE_KEY, 'Authorization': f'Bearer {SERVICE_KEY}', 'Content-Type': 'application/pdf'},
        data=data,
    )
    if up.status_code >= 300:
        errors.append({'id': file_id, 'error': f'upload failed {up.status_code}: {up.text[:200]}'})
        continue

    patch = requests.patch(
        f'{SUPABASE_URL}/rest/v1/legal_files',
        headers=REST_HEADERS,
        params={'id': f'eq.{file_id}'},
        json={
            'storage_path': new_storage_path,
            'original_filename': p['file'],
            'mime_type': 'application/pdf',
            'file_size': len(data),
            'file_hash': file_hash,
        },
    )
    if patch.status_code >= 300:
        requests.delete(
            f'{SUPABASE_URL}/storage/v1/object/{BUCKET}/{new_storage_path}',
            headers={'apikey': SERVICE_KEY, 'Authorization': f'Bearer {SERVICE_KEY}'},
        )
        errors.append({'id': file_id, 'error': f'db update failed {patch.status_code}: {patch.text[:200]}'})
        continue

    old_path = row['storage_path']
    if old_path and old_path != new_storage_path:
        requests.delete(
            f'{SUPABASE_URL}/storage/v1/object/{BUCKET}/{old_path}',
            headers={'apikey': SERVICE_KEY, 'Authorization': f'Bearer {SERVICE_KEY}'},
        )
    ok += 1

print('replaced ok:', ok)
print('errors:', len(errors))
for e in errors:
    print(' ', e)
