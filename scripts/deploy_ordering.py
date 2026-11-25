"""Deploy horizontal ordering with every bound form and the stock child process."""
from pathlib import Path
import sys, uuid, urllib.request
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'services/inventory-service'))
import worker,connect_f2

def deployment_files():
 folder=ROOT/'camunda/f2'
 return [folder/'processes'/name for name in ('place-order-horizontal.bpmn','check-product-stock-status.bpmn')]+sorted((folder/'forms').glob('*.form'))

def deployment_body():
 boundary='ordering-'+uuid.uuid4().hex;body=bytearray()
 files=deployment_files()
 for path in files:
  body.extend(('--'+boundary+'\r\nContent-Disposition: form-data; name="resources"; filename="'+path.name+'"\r\nContent-Type: application/octet-stream\r\n\r\n').encode());body.extend(path.read_bytes());body.extend(b'\r\n')
 body.extend(('--'+boundary+'--\r\n').encode())
 return boundary,bytes(body)

def main():
 connect_f2.load_credentials(Path.home()/'Downloads/daesd-omar-f2-worker-springboot.properties')
 worker.os.environ.setdefault('CAMUNDA_REST_ADDRESS',connect_f2.ENDPOINT)
 base=worker.setting('CAMUNDA_REST_ADDRESS','ZEEBE_REST_ADDRESS').rstrip('/').removesuffix('/v2')
 if base!=connect_f2.ENDPOINT:raise ValueError('Unexpected target cluster')
 worker.request('/topology')
 boundary,body=deployment_body()
 req=urllib.request.Request(base+'/v2/deployments',bytes(body),{'Authorization':worker.authorization_header(),'Content-Type':'multipart/form-data; boundary='+boundary})
 with urllib.request.urlopen(req,timeout=45) as response:print(response.read().decode())
if __name__=='__main__':main()
