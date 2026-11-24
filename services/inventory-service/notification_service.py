"""Local simulated Notification Service with durable, idempotent receipts.

Receives synthetic marketplace events over HTTP; never sends email or SMS.
"""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sqlite3

class Receipts:
    def __init__(self,path):
        self.db=sqlite3.connect(path)
        self.db.execute('CREATE TABLE IF NOT EXISTS receipts(id TEXT PRIMARY KEY, event TEXT NOT NULL, received_at TEXT DEFAULT CURRENT_TIMESTAMP)')
        self.db.commit()

    def accept(self,payload):
        ident=payload.get('id');event=payload.get('event')
        if not isinstance(ident,str) or not ident.strip() or not isinstance(event,dict):
            raise ValueError('id and event are required')
        if event.get('type') not in ('correction-requested','low-stock','out-of-stock'):
            raise ValueError('Unsupported notification type')
        text=json.dumps(event,sort_keys=True)
        with self.db:
            prior=self.db.execute('SELECT event FROM receipts WHERE id=?',(ident,)).fetchone()
            if prior and prior[0]!=text:raise ValueError('Event id reused with different content')
            self.db.execute('INSERT OR IGNORE INTO receipts(id,event) VALUES (?,?)',(ident,text))
        return {'accepted':True,'id':ident,'duplicate':prior is not None,'channel':'simulation'}

def handler_for(path):
    class Handler(BaseHTTPRequestHandler):
        def reply(self,status,body):
            data=json.dumps(body).encode()
            self.send_response(status);self.send_header('Content-Type','application/json')
            self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)

        def do_GET(self):
            self.reply(200,{'service':'daesd-notification-simulation','status':'ready'}) if self.path=='/health' else self.reply(404,{'error':'Not found'})

        def do_POST(self):
            if self.path!='/notifications':self.reply(404,{'error':'Not found'});return
            store=None
            try:
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=65536:raise ValueError('Invalid request size')
                payload=json.loads(self.rfile.read(size))
                if not isinstance(payload,dict):raise ValueError('Expected JSON object')
                store=Receipts(path);self.reply(200,store.accept(payload))
            except (ValueError,TypeError) as exc:self.reply(400,{'error':str(exc)})
            finally:
                if store:store.db.close()

        def log_message(self,*args):pass
    return Handler

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--db',type=Path,default=Path(__file__).with_name('notification-receipts.sqlite3'))
    args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',8765),handler_for(str(args.db)))
    print('Simulated Notification Service listening on 127.0.0.1:8765',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()

