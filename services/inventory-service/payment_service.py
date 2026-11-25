"""Local payment simulation: durable authorisation/capture/void; no money or cards."""
import argparse,json,sqlite3
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
class Payments:
 def __init__(self,path):
  self.db=sqlite3.connect(path);self.db.execute('CREATE TABLE IF NOT EXISTS payments(id TEXT PRIMARY KEY, details TEXT NOT NULL, status TEXT NOT NULL)');self.db.commit()
 def apply(self,p):
  ident=p.get('orderId');action=p.get('action');details=json.dumps({'productId':p.get('productId'),'quantity':p.get('purchasedQuantity'),'outcome':p.get('demoPaymentOutcome')},sort_keys=True)
  if not isinstance(ident,str) or not ident.strip() or action not in ('authorize','capture','void'):raise ValueError('Valid orderId and action required')
  with self.db:
   self.db.execute('BEGIN IMMEDIATE');prior=self.db.execute('SELECT details,status FROM payments WHERE id=?',(ident,)).fetchone()
   if prior and prior[0]!=details:raise ValueError('Order reference reused with different details')
   if action=='authorize':
    if p.get('demoPaymentOutcome') not in ('approve','decline'):raise ValueError('Choose approve or decline')
    status=prior[1] if prior else ('authorized' if p['demoPaymentOutcome']=='approve' else 'declined')
   else:
    if not prior:raise ValueError('Authorize first')
    status=prior[1];target='captured' if action=='capture' else 'voided'
    if status=='authorized':status=target
    elif status!=target and status!='declined':raise ValueError('Invalid payment transition')
   self.db.execute('INSERT OR REPLACE INTO payments VALUES (?,?,?)',(ident,details,status))
  return {'orderId':ident,'paymentAuthorized':status in ('authorized','captured'),'paymentStatus':status,'simulation':True}
def handler_for(path):
 class Handler(BaseHTTPRequestHandler):
  def reply(self,status,value):
   data=json.dumps(value).encode();self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
  def do_GET(self):self.reply(200,{'service':'daesd-payment-simulation'}) if self.path=='/health' else self.reply(404,{})
  def do_POST(self):
   if self.path!='/payments':self.reply(404,{});return
   store=None
   try:
    n=int(self.headers.get('Content-Length',0))
    if not 0<n<=65536:raise ValueError('Invalid request size')
    payload=json.loads(self.rfile.read(n))
    if not isinstance(payload,dict):raise ValueError('Expected object')
    store=Payments(path);self.reply(200,store.apply(payload))
   except (ValueError,TypeError) as exc:self.reply(400,{'error':str(exc)})
   finally:
    if store:store.db.close()
  def log_message(self,*args):pass
 return Handler
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--db',default=str(Path(__file__).with_name('payment-receipts.sqlite3')));args=parser.parse_args()
 server=ThreadingHTTPServer(('127.0.0.1',8766),handler_for(args.db));print('Simulated Payment Service ready on 127.0.0.1:8766',flush=True)
 try:server.serve_forever()
 except KeyboardInterrupt:pass
 finally:server.server_close()
