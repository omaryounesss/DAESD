"""F2 demonstration catalogue and Camunda 8 REST worker (Python 3.12, stdlib).

F1 publication and F2 inventory share this worker and its SQLite catalogue.
Run only one worker against a given catalogue database.
"""
import argparse
import base64
from datetime import date, datetime, timezone, timedelta
import json
import os
from pathlib import Path
import sqlite3
import time
import urllib.request
import urllib.error
import urllib.parse
import uuid

_oauth_token=None
_oauth_expires=0

def setting(name,alias=None,default=None):
    return os.environ.get(name) or (os.environ.get(alias) if alias else None) or default

def authorization_header():
    """Use existing API credentials; tokens stay in this process's memory."""
    global _oauth_token,_oauth_expires
    client=setting('CAMUNDA_CLIENT_ID','ZEEBE_CLIENT_ID')
    secret=setting('CAMUNDA_CLIENT_SECRET','ZEEBE_CLIENT_SECRET')
    if client and secret:
        if not _oauth_token or time.monotonic()>=_oauth_expires:
            endpoint=setting('CAMUNDA_OAUTH_URL','ZEEBE_AUTHORIZATION_SERVER_URL',
                             'https://login.cloud.camunda.io/oauth/token')
            if urllib.parse.urlparse(endpoint).scheme!='https':
                raise ValueError('OAuth endpoint must use HTTPS')
            body=urllib.parse.urlencode({'grant_type':'client_credentials','client_id':client,
                'client_secret':secret,'audience':setting('CAMUNDA_TOKEN_AUDIENCE','ZEEBE_TOKEN_AUDIENCE','zeebe.camunda.io')}).encode()
            req=urllib.request.Request(endpoint,body,{'Content-Type':'application/x-www-form-urlencoded'})
            with urllib.request.urlopen(req,timeout=20) as response:token=json.loads(response.read())
            _oauth_token=token['access_token']
            _oauth_expires=time.monotonic()+max(1,float(token.get('expires_in',300))-30)
        return 'Bearer '+_oauth_token
    if os.environ.get('CAMUNDA_ACCESS_TOKEN'):return 'Bearer '+os.environ['CAMUNDA_ACCESS_TOKEN']
    if os.environ.get('CAMUNDA_USERNAME'):
        raw=os.environ['CAMUNDA_USERNAME']+':'+os.environ.get('CAMUNDA_PASSWORD','')
        return 'Basic '+base64.b64encode(raw.encode()).decode()
    return None

KINDS = ('prepare-update','validate-quantity','validate-season','save-update','reduce-stock',
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
        CREATE TABLE IF NOT EXISTS season_schedule(
          product_id TEXT NOT NULL, season_version INTEGER NOT NULL,
          kind TEXT NOT NULL, due TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending',
          PRIMARY KEY(product_id,season_version,kind));
        CREATE TABLE IF NOT EXISTS season_events(
          product_id TEXT NOT NULL, season_version INTEGER NOT NULL, kind TEXT NOT NULL,
          due TEXT NOT NULL, applied_at TEXT NOT NULL, available INTEGER NOT NULL,
          quantity INTEGER NOT NULL,
          PRIMARY KEY(product_id,season_version,kind));
        ''')
        # Upgrade existing demo catalogues without discarding products or job history.
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            for (body,) in self.db.execute('SELECT body FROM products').fetchall():
                product=json.loads(body)
                if 'seasonVersion' not in product:
                    product['seasonVersion']=1
                    self.save(product)
                    self._schedule(product)

    def _schedule(self,p):
        """Called inside the same transaction that persists the changed dates."""
        self.db.execute("UPDATE season_schedule SET status='cancelled' WHERE product_id=? AND status='pending'",
                        (p['productId'],))
        boundaries={'start':p['availableFrom'],
                    'end':str(date.fromisoformat(p['availableUntil'])+timedelta(days=1))}
        for kind,due in boundaries.items():
            self.db.execute('INSERT INTO season_schedule(product_id,season_version,kind,due) VALUES (?,?,?,?)',
                            (p['productId'],p['seasonVersion'],kind,due))

    def apply_due_seasons(self,now=None):
        """Apply persistent due actions, rechecking current dates and stock.

        Service-side scheduler only: it does not start or alter Camunda routes.
        Date boundaries are UTC, and end dates are inclusive. A restart processes
        missed boundaries using current state, never enabling a season already over.
        """
        instant=now or datetime.now(timezone.utc)
        if instant.tzinfo is None:raise ValueError('Scheduler time must include a timezone')
        instant=instant.astimezone(timezone.utc);today=instant.date()
        applied=[]
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            due=self.db.execute("SELECT product_id,season_version,kind,due FROM season_schedule WHERE status='pending' AND due<=? ORDER BY due,product_id,kind",
                                (str(today),)).fetchall()
            for pid,version,kind,boundary in due:
                p=self.get(pid)
                expected=p['availableFrom'] if kind=='start' else str(date.fromisoformat(p['availableUntil'])+timedelta(days=1))
                if version!=p['seasonVersion'] or boundary!=expected:
                    self.db.execute("UPDATE season_schedule SET status='cancelled' WHERE product_id=? AND season_version=? AND kind=?",
                                    (pid,version,kind));continue
                p['withinSeason']=date.fromisoformat(p['availableFrom'])<=today<=date.fromisoformat(p['availableUntil'])
                p['available']=p['quantity']>0 and p['withinSeason']
                self.save(p)
                self.db.execute('INSERT OR IGNORE INTO season_events VALUES (?,?,?,?,?,?,?)',
                    (pid,version,kind,boundary,instant.isoformat(),int(p['available']),p['quantity']))
                self.db.execute("UPDATE season_schedule SET status='completed' WHERE product_id=? AND season_version=? AND kind=?",
                                (pid,version,kind))
                applied.append({'productId':pid,'seasonVersion':version,'boundary':kind,
                                'available':p['available'],'quantity':p['quantity']})
        return applied

    def get(self,pid):
        row=self.db.execute('SELECT body FROM products WHERE id=?',(pid,)).fetchone()
        if not row:raise ValueError('Unknown productId; publish through F1 or seed a demo product first')
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
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            previous=self.db.execute('SELECT body FROM products WHERE id=?',(p['productId'],)).fetchone()
            p['seasonVersion']=json.loads(previous[0]).get('seasonVersion',0)+1 if previous else 1
            self.save(p);self._schedule(p)

    def handle(self,key,kind,v,today=None):
        """Commit business effects and cached response in one transaction.

        A retry of the same Zeebe job does not repeat a stock decrement or increment
        a correction counter. Paid orders are also deduplicated by orderId.
        """
        now=today or datetime.now(timezone.utc).date()
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            row=self.db.execute('SELECT result FROM jobs WHERE id=?',(str(key),)).fetchone()
            if row:return json.loads(row[0])
            out=self._handle(str(key),kind,v,now)
            self.db.execute('INSERT INTO jobs VALUES (?,?)',(str(key),json.dumps(out)))
        return out

    def _handle(self,key,kind,v,now):
        if kind=='prepare-update':
            products=[json.loads(row[0]) for row in self.db.execute('SELECT body FROM products ORDER BY id')]
            return {'updateId':'UI-'+uuid.uuid4().hex,'correctionAttempts':0,
                    'validationErrors':[],
                    'productOptions':[{'label':f"{p.get('name',p['productId'])} - {p['productId']} (stock {p['quantity']})",
                                       'value':p['productId']} for p in products]}
        if kind=='publish-product':
            if v.get('productDetailsValid') is not True:
                raise ValueError('F1 publication requires validated product details')
            listing=v.get('listingId')
            product=dict(v.get('product') or {})
            if not isinstance(listing,str) or not listing.strip() or product.get('listingId')!=listing:
                raise ValueError('F1 product must have a matching listingId')
            if not isinstance(v.get('traceabilityRecord'),dict) or not v['traceabilityRecord']:
                raise ValueError('F1 publication requires a traceability record')
            pid=v.get('productId') or listing
            if not isinstance(pid,str) or not pid.strip():
                raise ValueError('productId must be a nonempty string')
            row=self.db.execute('SELECT body FROM products WHERE id=?',(pid,)).fetchone()
            if row:
                existing=json.loads(row[0])
                if existing.get('listingId')!=listing:
                    raise ValueError('productId already belongs to another catalogue product')
                # A publication retry must never reset stock changed by F2.
                product=existing
            else:
                if not integer(product.get('quantity')):
                    raise ValueError('Invalid F1 quantity')
                start=date.fromisoformat(product['availableFrom'])
                end=date.fromisoformat(product['availableUntil'])
                if end<start:raise ValueError('Invalid F1 season dates')
                threshold=product.get('lowStockThreshold',5)
                if not integer(threshold) or threshold==0:
                    raise ValueError('Invalid low-stock threshold')
                product.update(productId=pid,listingId=listing,revision=1,seasonVersion=1,
                    lowStockThreshold=threshold,traceabilityRecord=v['traceabilityRecord'])
                product['withinSeason']=start<=now<=end
                product['available']=product['quantity']>0 and product['withinSeason']
                product['publishedAt']=datetime.now(timezone.utc).isoformat()
                self.save(product)
                self._schedule(product)
            return {'productId':pid,'listingStatus':'Published','cataloguePersisted':True,
                    'catalogueEntry':{'product':product,'savedAt':product['publishedAt']}}
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
            changed=(p['availableFrom'],p['availableUntil'])!=(str(start),str(end))
            p.update(quantity=q,availableFrom=str(start),availableUntil=str(end),revision=p['revision']+1)
            if changed:
                p['seasonVersion']+=1
                self._schedule(p)
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

def request(path,body=None,method=None):
    base=setting('CAMUNDA_REST_ADDRESS','ZEEBE_REST_ADDRESS','http://localhost:8080').rstrip('/')
    if not base.endswith('/v2'):base+='/v2'
    headers={'Content-Type':'application/json'}
    auth=authorization_header()
    if auth:headers['Authorization']=auth
    data=None if body is None else json.dumps(body).encode()
    req=urllib.request.Request(base+path,data,headers,method=method)
    with urllib.request.urlopen(req,timeout=30) as response:
        return json.loads(response.read() or b'{}')

def run(catalogue):
    while True:
        try:
            for action in catalogue.apply_due_seasons():
                print('Season action: '+json.dumps(action),flush=True)
            for kind in ('publish-product',)+KINDS:
                catalogue.apply_due_seasons()
                job_type='f1-publish-product' if kind=='publish-product' else 'f2-'+kind
                jobs=request('/jobs/activation',{'type':job_type,'worker':'daesd-f2',
                     'timeout':30000,'maxJobsToActivate':1,'requestTimeout':-1}).get('jobs',[])
                for job in jobs:
                    key=job['jobKey']
                    try:
                        result=catalogue.handle(key,kind,job.get('variables',{}))
                        request(f'/jobs/{key}/completion',{'variables':result})
                        print(f'Completed F2 job {key} ({kind}) for {result.get("productId",job.get("variables",{}).get("productId","unknown"))}',flush=True)
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
    parser.add_argument('--scheduler-once',action='store_true',help='Apply due catalogue schedules once without connecting to Camunda')
    args=parser.parse_args();catalogue=Catalogue(args.db)
    if args.seed:catalogue.seed(json.loads(args.seed.read_text()));print('Demo product seeded.')
    elif args.scheduler_once:print(json.dumps(catalogue.apply_due_seasons(),indent=2))
    else:run(catalogue)

