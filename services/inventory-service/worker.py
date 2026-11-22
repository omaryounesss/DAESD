"""F2 demonstration catalogue and Camunda 8 REST worker (Python 3.12, stdlib).

SQLite state is local to this demo worker. F1 is not connected or modified.
Run only one worker against a given catalogue database.
"""
import argparse
import base64
from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
import sqlite3
import time
import urllib.request
import urllib.error

KINDS = ('validate-quantity','validate-season','save-update','reduce-stock',
         'available','unavailable','notify-low','notify-zero','request-correction',
         'save-final','retrieve-stock')

def integer(n):
    return isinstance(n,(int,float)) and not isinstance(n,bool) and n >= 0 and int(n)==n

class Catalogue:
    def __init__(self,path='f2-catalogue.sqlite3'):
        self.db=sqlite3.connect(path)
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS products(id TEXT PRIMARY KEY, body TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, result TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS orders(id TEXT PRIMARY KEY, product_id TEXT NOT NULL, purchased INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS notifications(id TEXT PRIMARY KEY, body TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS outbox(id TEXT PRIMARY KEY, body TEXT NOT NULL, sent INTEGER DEFAULT 0);
        ''')

    def get(self,pid):
        row=self.db.execute('SELECT body FROM products WHERE id=?',(pid,)).fetchone()
        if not row:raise ValueError('Unknown productId; seed an existing published product first')
        return json.loads(row[0])

    def save(self,p):
        self.db.execute('INSERT OR REPLACE INTO products VALUES (?,?)',(p['productId'],json.dumps(p)))

    def seed(self,p):
        if not integer(p.get('quantity')):raise ValueError('quantity must be a nonnegative integer')
        start,end=date.fromisoformat(p['availableFrom']),date.fromisoformat(p['availableUntil'])
        if end<start:raise ValueError('Season end precedes start')
        if not integer(p.get('lowStockThreshold',5)) or p.get('lowStockThreshold',5)==0:raise ValueError('Invalid threshold')
        p={**p,'lowStockThreshold':p.get('lowStockThreshold',5),'available':False,'revision':1}
        p['withinSeason']=start<=datetime.now(timezone.utc).date()<=end
        p['available']=p['quantity']>0 and p['withinSeason']
        with self.db:self.save(p)

    def handle(self,key,kind,v,today=None):
        """Commit business effects and cached response in one transaction.

        A retry of the same Zeebe job does not repeat a stock decrement or increment
        a correction counter. Paid orders are also deduplicated by orderId.
        """
        row=self.db.execute('SELECT result FROM jobs WHERE id=?',(str(key),)).fetchone()
        if row:return json.loads(row[0])
        now=today or datetime.now(timezone.utc).date()
        with self.db:
            out=self._handle(str(key),kind,v,now)
            self.db.execute('INSERT INTO jobs VALUES (?,?)',(str(key),json.dumps(out)))
        return out

    def _handle(self,key,kind,v,now):
        if kind=='validate-quantity':
            errors=[]
            try:self.get(v.get('productId'))
            except ValueError:errors.append('Product does not exist in the catalogue.')
            if not v.get('updateId'):errors.append('updateId is required for correction correlation.')
            if not integer(v.get('quantity')):errors.append('Quantity must be a nonnegative whole number.')
            return {'validationErrors':errors,'quantityValid':not errors}
        if kind=='validate-season':
            errors=list(v.get('validationErrors',[]))
            try:
                start,end=date.fromisoformat(v['availableFrom']),date.fromisoformat(v['availableUntil'])
                if end<start:errors.append('Season end must be on or after season start.')
            except (KeyError,TypeError,ValueError):errors.append('Season dates must use YYYY-MM-DD.')
            valid=not errors
            return {'validationErrors':errors,'updateValid':valid,
                    'correctionAttempts':v.get('correctionAttempts',0)+(0 if valid else 1)}
        if kind=='request-correction':
            if not v.get('updateId'):raise ValueError('updateId is required')
            self.db.execute('INSERT OR IGNORE INTO notifications VALUES (?,?)',
                (key,json.dumps({'type':'correction-requested','productId':v.get('productId'),
                 'updateId':v['updateId'],'validationErrors':v.get('validationErrors',[])})))
            return {}
        pid=v.get('productId')
        if not pid and kind in ('retrieve-stock','unavailable'):
            pid=os.environ.get('F2_TIMER_PRODUCT_ID')
            if not pid:raise ValueError('Set F2_TIMER_PRODUCT_ID for original seasonal timer routes')
        p=self.get(pid)
        if kind=='save-update':
            # Recheck independently; a forged process flag cannot persist invalid data.
            q=v.get('quantity');start=date.fromisoformat(v['availableFrom']);end=date.fromisoformat(v['availableUntil'])
            if not integer(q) or end<start:raise ValueError('Invalid update cannot be saved')
            p.update(quantity=q,availableFrom=str(start),availableUntil=str(end),revision=p['revision']+1)
        elif kind=='reduce-stock':
            order=v.get('orderId');n=v.get('purchasedQuantity')
            if not order or not integer(n) or n==0:raise ValueError('orderId and positive purchasedQuantity required')
            prior=self.db.execute('SELECT product_id,purchased FROM orders WHERE id=?',(str(order),)).fetchone()
            if prior and prior!=(pid,n):raise ValueError('orderId reused with different purchase details')
            if not prior:
                if n>p['quantity']:raise ValueError('Insufficient stock; no negative quantity is permitted')
                p['quantity']-=n;p['revision']+=1
                self.db.execute('INSERT INTO orders VALUES (?,?,?)',(str(order),pid,n))
        elif kind in ('notify-low','notify-zero'):
            actual='out-of-stock' if p['quantity']==0 else ('low-stock' if p['quantity']<p['lowStockThreshold'] else None)
            expected='low-stock' if kind=='notify-low' else 'out-of-stock'
            if actual==expected:
                nid=f"{pid}:{p['revision']}:{actual}"
                self.db.execute('INSERT OR IGNORE INTO notifications VALUES (?,?)',
                                (nid,json.dumps({'productId':pid,'type':actual,'quantity':p['quantity']})))
        elif kind not in ('available','unavailable','retrieve-stock','save-final'):
            raise ValueError('Unknown job type '+kind)
        # Re-evaluate current catalogue state rather than trusting stale workflow variables.
        p['withinSeason']=date.fromisoformat(p['availableFrom'])<=now<=date.fromisoformat(p['availableUntil'])
        p['available']=p['quantity']>0 and p['withinSeason']
        self.save(p)
        return {k:p[k] for k in ('productId','quantity','availableFrom','availableUntil','lowStockThreshold','withinSeason','available','revision')}

def request(path,body):
    base=os.environ.get('CAMUNDA_REST_ADDRESS','http://localhost:8080').rstrip('/')
    if not base.endswith('/v2'):base+='/v2'
    headers={'Content-Type':'application/json'}
    if os.environ.get('CAMUNDA_ACCESS_TOKEN'):headers['Authorization']='Bearer '+os.environ['CAMUNDA_ACCESS_TOKEN']
    elif os.environ.get('CAMUNDA_USERNAME'):
        raw=os.environ['CAMUNDA_USERNAME']+':'+os.environ.get('CAMUNDA_PASSWORD','')
        headers['Authorization']='Basic '+base64.b64encode(raw.encode()).decode()
    req=urllib.request.Request(base+path,json.dumps(body).encode(),headers)
    with urllib.request.urlopen(req,timeout=30) as response:
        return json.loads(response.read() or b'{}')

def run(catalogue):
    while True:
        try:
            for kind in KINDS:
                jobs=request('/jobs/activation',{'type':'f2-'+kind,'worker':'daesd-f2',
                     'timeout':30000,'maxJobsToActivate':10,'requestTimeout':0}).get('jobs',[])
                for job in jobs:
                    key=job['jobKey']
                    try:
                        result=catalogue.handle(key,kind,job.get('variables',{}))
                        request(f'/jobs/{key}/completion',{'variables':result})
                    except Exception as exc:
                        print(f'F2 job {key} ({kind}): {exc}',flush=True)
                        request(f'/jobs/{key}/failure',{'retries':max(0,job.get('retries',1)-1),
                                                     'errorMessage':str(exc),'retryBackOff':5000})
            time.sleep(1)
        except (urllib.error.URLError,TimeoutError) as exc:
            print('Camunda connection unavailable: '+str(exc),flush=True);time.sleep(5)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--db',default='f2-catalogue.sqlite3')
    parser.add_argument('--seed',type=Path,help='Seed a demo published product from JSON and exit')
    args=parser.parse_args();catalogue=Catalogue(args.db)
    if args.seed:catalogue.seed(json.loads(args.seed.read_text()));print('Demo product seeded.')
    else:run(catalogue)
