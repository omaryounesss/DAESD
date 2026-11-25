"""Start the existing Java certification service using existing cluster credentials."""
from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'services/inventory-service'))
import connect_f2

def main():
    connect_f2.load_credentials(Path.home() / 'Downloads/daesd-omar-f2-worker-springboot.properties')
    client_id = os.environ.get('CAMUNDA_CLIENT_ID') or os.environ.get('ZEEBE_CLIENT_ID')
    secret = os.environ.get('CAMUNDA_CLIENT_SECRET') or os.environ.get('ZEEBE_CLIENT_SECRET')
    if not client_id or not secret:
        raise ValueError('Existing client ID and secret are required; no new credentials are created.')
    child_env = os.environ.copy()
    child_env.update(CAMUNDA_CLUSTER_ID='848240b1-573c-4a07-bd52-723bea5b23b7',
                     CAMUNDA_CLUSTER_REGION='lhr-1', ZEEBE_CLIENT_ID=client_id,
                     ZEEBE_CLIENT_SECRET=secret)
    print('Starting the existing certification service for UWE Frenchay 2026. Credentials stay in process memory.', flush=True)
    return subprocess.call(['cmd.exe', '/d', '/c', 'mvn', '-o', 'compile', 'exec:java'],
                           cwd=Path(__file__).resolve().parent, env=child_env)

if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError) as exc:
        print(f'Certification setup failed: {exc}', file=sys.stderr)
        sys.exit(1)

