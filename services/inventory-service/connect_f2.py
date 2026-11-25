"""Interactive F2 connection launcher. Existing credentials only; no secrets saved."""
import argparse
import getpass
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request
import subprocess
import time
import worker

ENDPOINT='https://lhr-1.api.camunda.io/848240b1-573c-4a07-bd52-723bea5b23b7'
ALLOWED={'CAMUNDA_REST_ADDRESS','ZEEBE_REST_ADDRESS','CAMUNDA_CLIENT_ID','ZEEBE_CLIENT_ID',
 'CAMUNDA_CLIENT_SECRET','ZEEBE_CLIENT_SECRET','CAMUNDA_OAUTH_URL','ZEEBE_AUTHORIZATION_SERVER_URL',
 'CAMUNDA_TOKEN_AUDIENCE','ZEEBE_TOKEN_AUDIENCE','CAMUNDA_ACCESS_TOKEN','F2_TIMER_PRODUCT_ID'}

def load_credentials(path):
    # Parse assignments as data. Never run a downloaded shell/env file as code.
    aliases={'camunda.client.auth.client-id':'CAMUNDA_CLIENT_ID',
             'camunda.client.auth.client-secret':'CAMUNDA_CLIENT_SECRET'}
    for line in Path(path).read_text(encoding='utf-8-sig').splitlines():
        line=line.strip()
        if not line or line.startswith('#'):continue
        if line.startswith('export '):line=line[7:]
        if '=' not in line:continue
        key,value=line.split('=',1);key=key.strip();value=value.strip()
        if key=='camunda.client.cloud.cluster-id' and value!='848240b1-573c-4a07-bd52-723bea5b23b7':
            raise ValueError('Credentials belong to a different cluster')
        key=aliases.get(key,key)
        if len(value)>=2 and value[0]==value[-1] and value[0] in ('"',"'"):value=value[1:-1]
        if key in ALLOWED:os.environ[key]=value

def main():
    parser=argparse.ArgumentParser(description='Connect the F2 worker to UWE Frenchay 2026')
    parser.add_argument('--credentials',type=Path,help='Existing Camunda .env file, parsed without execution')
    parser.add_argument('--check-only',action='store_true')
    parser.add_argument('--db',type=Path,default=Path(__file__).with_name('f2-catalogue.sqlite3'))
    args=parser.parse_args()
    if args.credentials:load_credentials(args.credentials)
    if not worker.setting('CAMUNDA_REST_ADDRESS','ZEEBE_REST_ADDRESS'):os.environ['CAMUNDA_REST_ADDRESS']=ENDPOINT
    if not worker.setting('CAMUNDA_CLIENT_ID','ZEEBE_CLIENT_ID') and not os.environ.get('CAMUNDA_ACCESS_TOKEN'):
        print('Use EXISTING Orchestration Cluster API credentials for UWE Frenchay 2026.')
        os.environ['CAMUNDA_CLIENT_ID']=input('Client ID: ').strip()
    if worker.setting('CAMUNDA_CLIENT_ID','ZEEBE_CLIENT_ID') and not worker.setting('CAMUNDA_CLIENT_SECRET','ZEEBE_CLIENT_SECRET'):
        os.environ['CAMUNDA_CLIENT_SECRET']=getpass.getpass('Client secret (hidden; not saved): ')
    base=worker.setting('CAMUNDA_REST_ADDRESS','ZEEBE_REST_ADDRESS')
    if base.rstrip('/').removesuffix('/v2')!=ENDPOINT:
        raise ValueError('Credentials target a different cluster; use the UWE Frenchay 2026 REST address')
    print('Checking UWE Frenchay 2026 REST connection...',flush=True)
    topology=worker.request('/topology')
    if not isinstance(topology,dict):raise ValueError('Unexpected topology response')
    print('CONNECTED: the cluster accepted an authenticated topology request.',flush=True)
    if args.check_only:return
    catalogue=worker.Catalogue(str(args.db))
    # Only older deployed timer instances use this fallback. New seasonal
    # messages always carry their productId; startup never inserts demo stock.
    os.environ.setdefault('F2_TIMER_PRODUCT_ID','P1')
    print('Worker running. Keep this terminal open; Ctrl+C stops it. No credentials are written to disk.',flush=True)
    notification_process=None
    payment_process=None
    def check_notification_service():
        with urllib.request.urlopen('http://127.0.0.1:8765/health',timeout=2) as response:
            if json.loads(response.read()).get('service')!='daesd-notification-simulation':
                raise ValueError('Port 8765 is occupied by another service')
    try:
        try:check_notification_service()
        except urllib.error.URLError:
            notification_process=subprocess.Popen([sys.executable,'-u',str(Path(__file__).with_name('notification_service.py'))],
                creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            for attempt in range(20):
                try:check_notification_service();break
                except urllib.error.URLError:
                    if notification_process.poll() is not None:raise ValueError('Notification Service could not start; check port 8765')
                    time.sleep(0.1)
            else:raise ValueError('Notification Service did not become ready')
        print('NOTIFICATIONS: separate local simulated service is ready.',flush=True)
        def check_payment_service():
            with urllib.request.urlopen('http://127.0.0.1:8766/health',timeout=2) as response:
                if json.loads(response.read()).get('service')!='daesd-payment-simulation':
                    raise ValueError('Port 8766 is occupied by another service')
        try:check_payment_service()
        except urllib.error.URLError:
            payment_process=subprocess.Popen([sys.executable,'-u',str(Path(__file__).with_name('payment_service.py'))],
                creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0),stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            for attempt in range(20):
                try:check_payment_service();break
                except urllib.error.URLError:
                    if payment_process.poll() is not None:raise ValueError('Payment Service could not start; check port 8766')
                    time.sleep(0.1)
            else:raise ValueError('Payment Service did not become ready')
        print('PAYMENTS: separate local simulated service is ready; no real money.',flush=True)
        worker.run(catalogue)
    finally:
        if payment_process is not None:
            payment_process.terminate();payment_process.wait(timeout=5)
        if notification_process is not None:
            notification_process.terminate();notification_process.wait(timeout=5)

if __name__=='__main__':
    try:main()
    except KeyboardInterrupt:print('\nWorker stopped.')
    except urllib.error.HTTPError as exc:
        print(f'Connection rejected: HTTP {exc.code}. Check cluster API permissions and existing credentials.',file=sys.stderr);sys.exit(1)
    except (ValueError,OSError,KeyError) as exc:
        print(f'Connection/setup failed: {exc}',file=sys.stderr);sys.exit(1)
