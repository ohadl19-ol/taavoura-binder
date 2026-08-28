# -*- coding: utf-8 -*-
import json, os, re, hashlib, uuid, requests

ENV = {}
for line in open('/Users/ohadlevy/psika-north/.env.local', encoding='utf-8'):
    line = line.strip()
    if not line or line.startswith('#') or '=' not in line:
        continue
    k, v = line.split('=', 1)
    ENV[k.strip()] = v.strip()

SUPABASE_URL = ENV['NEXT_PUBLIC_SUPABASE_URL']
SERVICE_KEY = ENV['SUPABASE_SERVICE_ROLE_KEY']
BUCKET = 'legal-files'

HEADERS_REST = {
    'apikey': SERVICE_KEY,
    'Authorization': f'Bearer {SERVICE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation',
}

def normalize_case_number(raw):
    s = raw.strip()
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'\s*([/\\\-])\s*', r'\1', s)
    return s

def fetch_existing():
    r = requests.get(
        f'{SUPABASE_URL}/rest/v1/legal_files',
        headers={'apikey': SERVICE_KEY, 'Authorization': f'Bearer {SERVICE_KEY}'},
        params={'select': 'id,title,case_number,normalized_case_number,file_hash', 'deleted_at': 'is.null'},
    )
    r.raise_for_status()
    return r.json()

def upload_file(local_path, ext, mime):
    data = open(local_path, 'rb').read()
    file_hash = hashlib.sha256(data).hexdigest()
    storage_path = f'{uuid.uuid4()}.{ext}'
    r = requests.post(
        f'{SUPABASE_URL}/storage/v1/object/{BUCKET}/{storage_path}',
        headers={
            'apikey': SERVICE_KEY,
            'Authorization': f'Bearer {SERVICE_KEY}',
            'Content-Type': mime,
        },
        data=data,
    )
    if r.status_code >= 300:
        raise RuntimeError(f'storage upload failed {r.status_code}: {r.text[:300]}')
    return storage_path, file_hash, len(data)

def insert_record(title, case_number, storage_path, original_filename, mime, size, file_hash):
    record = {
        'title': title,
        'case_number': case_number,
        'normalized_case_number': normalize_case_number(case_number),
        'storage_path': storage_path,
        'original_filename': original_filename,
        'mime_type': mime,
        'file_size': size,
        'file_hash': file_hash,
    }
    r = requests.post(f'{SUPABASE_URL}/rest/v1/legal_files', headers=HEADERS_REST, json=record)
    if r.status_code >= 300:
        raise RuntimeError(f'insert failed {r.status_code}: {r.text[:300]}')
    return r.json()[0]['id']

if __name__ == '__main__':
    existing = fetch_existing()
    print('existing rows in vault:', len(existing))
    for e in existing[:10]:
        print(' ', e['case_number'], '|', e['title'][:40])
