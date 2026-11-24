"""Deploy connected F1 with the existing cluster credentials; no secrets saved."""
from pathlib import Path
import sys
import uuid
import urllib.request
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'services/inventory-service'))
import worker
import connect_f2

def main():
    credentials=Path.home()/'Downloads/daesd-omar-f2-worker-springboot.properties'
    connect_f2.load_credentials(credentials)
    worker.os.environ.setdefault('CAMUNDA_REST_ADDRESS',connect_f2.ENDPOINT)
    base=worker.setting('CAMUNDA_REST_ADDRESS','ZEEBE_REST_ADDRESS').rstrip('/').removesuffix('/v2')
    if base!=connect_f2.ENDPOINT:raise ValueError('Unexpected target cluster')
    worker.request('/topology')
    boundary='daesd-'+uuid.uuid4().hex
    body=bytearray()
    for path in sorted((ROOT/'camunda/f1').rglob('*')):
        if path.suffix not in ('.bpmn','.form'):continue
        body.extend(('--'+boundary+'\r\nContent-Disposition: form-data; name="resources"; filename="'+path.name+'"\r\nContent-Type: application/octet-stream\r\n\r\n').encode())
        body.extend(path.read_bytes());body.extend(b'\r\n')
    body.extend(('--'+boundary+'--\r\n').encode())
    req=urllib.request.Request(base+'/v2/deployments',bytes(body),{
        'Authorization':worker.authorization_header(),
        'Content-Type':'multipart/form-data; boundary='+boundary})
    with urllib.request.urlopen(req,timeout=60) as response:
        print(response.read().decode())
    print('Connected F1 deployed. Start a NEW F1 instance; existing instances keep their old version.')
if __name__=='__main__':main()

