import requests
from replace_with_pdfs import SUPABASE_URL, SERVICE_KEY

r = requests.get(
    f'{SUPABASE_URL}/rest/v1/legal_files',
    headers={'apikey': SERVICE_KEY, 'Authorization': f'Bearer {SERVICE_KEY}'},
    params={'select': 'id,mime_type,original_filename', 'deleted_at': 'is.null'},
)
rows = r.json()
from collections import Counter
print('total rows:', len(rows))
print(Counter(row['mime_type'] for row in rows))
