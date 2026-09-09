import sys, os, json, hashlib
sys.path.insert(0, os.path.abspath('.'))

from ml.training.dataset_builder import DatasetBuilder
from backend.app.services.replay_service import ReplayService

print('1. Generating benchmark dataset...')
df = DatasetBuilder.generate_synthetic_benchmark_data(n_samples=2500, random_seed=42)
os.makedirs('data/processed', exist_ok=True)
csv_path = 'data/processed/benchmark_dataset_v1.csv'
parquet_path = 'data/processed/benchmark_dataset_v1.parquet'
df.to_csv(csv_path, index=False)
df.to_parquet(parquet_path, index=False)
print(f'Saved {len(df)} samples to {csv_path} and {parquet_path}')

print('2. Generating case study data files...')
cases = [
    ('case_01_vizag_refinery', 'CASE-01-VIZAG'),
    ('case_02_jharia_coalfield', 'CASE-02-JHARIA'),
    ('case_03_morbi_ceramics', 'CASE-03-MORBI')
]

for folder, cid in cases:
    case_dir = os.path.join('data/cases', folder)
    os.makedirs(case_dir, exist_ok=True)
    meta = next((c for c in ReplayService.CASE_STUDIES if c['case_id'] == cid), {})
    steps = ReplayService.get_case_steps(cid)
    payload = {
        'case_metadata': meta,
        'steps_count': len(steps),
        'telemetry_steps': steps
    }
    target_json = os.path.join(case_dir, 'case_data.json')
    with open(target_json, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2)
    print(f'Saved {cid} telemetry to {target_json}')

print('3. Generating SHA-256 data manifest...')
manifest = {
    'manifest_version': '1.0.0',
    'generated_at': '2026-09-09T00:00:00Z',
    'system': 'THERMALIS-X SIH-26162',
    'assets': {}
}

def hash_file(filepath):
    sha = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()

files_to_hash = [
    csv_path,
    parquet_path,
    'data/cases/case_01_vizag_refinery/case_data.json',
    'data/cases/case_02_jharia_coalfield/case_data.json',
    'data/cases/case_03_morbi_ceramics/case_data.json'
]

for fp in files_to_hash:
    norm_fp = fp.replace('\\', '/')
    manifest['assets'][norm_fp] = {
        'sha256': hash_file(fp),
        'size_bytes': os.path.getsize(fp)
    }

os.makedirs('data/manifests', exist_ok=True)
with open('data/manifests/data_manifest.json', 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2)
with open('data_manifest.json', 'w', encoding='utf-8') as f:
    json.dump(manifest, f, indent=2)

print('Data assets and cryptographic manifest successfully generated!')
