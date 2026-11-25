"""Deploy exactly the two F2 BPMNs and three forms with existing credentials."""
from pathlib import Path
import sys
import uuid
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'services/inventory-service'))
import worker
import connect_f2

def deployment_body():
    files=[ROOT/'camunda/f2/processes'/name for name in
           ('inventory-seasonal-availability.bpmn','check-product-stock-status.bpmn')]
    files += [ROOT/'camunda/f2/forms'/name for name in
              ('f2-stock-update.form','f2-stock-correction.form','f2-inventory-review.form')]
    boundary='daesd-'+uuid.uuid4().hex
    body=bytearray()
    for path in files:
        body.extend(('--'+boundary+'\r\nContent-Disposition: form-data; name="resources"; filename="'+path.name+'"\r\nContent-Type: application/octet-stream\r\n\r\n').encode())
        body.extend(path.read_bytes());body.extend(b'\r\n')
    body.extend(('--'+boundary+'--\r\n').encode())
    return boundary,bytes(body)

def main():
    connect_f2.load_credentials(Path.home()/'Downloads/daesd-omar-f2-worker-springboot.properties')
    worker.os.environ.setdefault('CAMUNDA_REST_ADDRESS',connect_f2.ENDPOINT)
    base=worker.setting('CAMUNDA_REST_ADDRESS','ZEEBE_REST_ADDRESS').rstrip('/').removesuffix('/v2')
    if base!=connect_f2.ENDPOINT:raise ValueError('Unexpected target cluster')
    worker.request('/topology')
    boundary,body=deployment_body()
    req=urllib.request.Request(base+'/v2/deployments',body,{
        'Authorization':worker.authorization_header(),'Content-Type':'multipart/form-data; boundary='+boundary})
    with urllib.request.urlopen(req,timeout=60) as response:print(response.read().decode())
    print('DEPLOYED: two F2 processes and all three forms. Existing instances retain their old version.')

if __name__=='__main__':main()

