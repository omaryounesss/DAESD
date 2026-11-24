import importlib.util
from pathlib import Path
from datetime import date
import unittest

ROOT=Path(__file__).resolve().parents[1]
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'services/inventory-service'/file)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
w=module('delivery_worker','worker.py');n=module('notification_service','notification_service.py')

class NotificationDeliveryTests(unittest.TestCase):
    def setUp(self):
        self.c=w.Catalogue(':memory:');self.receipts=n.Receipts(':memory:')
        self.c.seed({'productId':'P1','quantity':2,'availableFrom':'2026-11-01','availableUntil':'2026-12-31'})

    def test_record_and_outbox_are_committed_together_and_delivery_is_idempotent(self):
        self.c.handle('low','notify-low',{'productId':'P1'},date(2026,11,24))
        self.c.handle('again','notify-low',{'productId':'P1'},date(2026,11,24))
        self.assertEqual(1,self.c.db.execute('SELECT count(*) FROM notifications').fetchone()[0])
        self.assertEqual(1,self.c.db.execute('SELECT count(*) FROM outbox').fetchone()[0])
        self.c.dispatch_outbox(lambda body:None,self.receipts.accept,now=100)
        self.assertEqual(1,self.c.db.execute('SELECT sent FROM outbox').fetchone()[0])
        self.assertEqual(1,self.receipts.db.execute('SELECT count(*) FROM receipts').fetchone()[0])

    def test_lost_response_retries_without_duplicate_service_receipt_or_stock_change(self):
        self.c.handle('low','notify-low',{'productId':'P1'},date(2026,11,24))
        before=self.c.get('P1')
        def lost(body):self.receipts.accept(body);raise OSError('response lost')
        self.c.dispatch_outbox(lambda body:None,lost,now=100)
        self.assertEqual((0,1),self.c.db.execute('SELECT sent,attempts FROM outbox').fetchone())
        self.c.dispatch_outbox(lambda body:None,self.receipts.accept,now=101)
        self.assertEqual(0,self.c.db.execute('SELECT sent FROM outbox').fetchone()[0])
        self.c.dispatch_outbox(lambda body:None,self.receipts.accept,now=103)
        self.assertEqual(1,self.receipts.db.execute('SELECT count(*) FROM receipts').fetchone()[0])
        self.assertEqual(before,self.c.get('P1'))

    def test_service_rejects_conflicting_receipt_id(self):
        payload={'id':'N1','event':{'type':'low-stock','quantity':2}}
        self.receipts.accept(payload)
        with self.assertRaises(ValueError):self.receipts.accept({'id':'N1','event':{'type':'low-stock','quantity':1}})

if __name__=='__main__':unittest.main()

