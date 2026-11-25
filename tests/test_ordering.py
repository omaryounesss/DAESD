import importlib.util
from pathlib import Path
from datetime import date
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('ordering_worker',ROOT/'services/inventory-service/worker.py')
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
class OrderingTests(unittest.TestCase):
 def setUp(self):
  self.c=w.Catalogue(':memory:');self.c.seed({'productId':'P1','quantity':4,'availableFrom':'2026-01-01','availableUntil':'2099-12-31','lowStockThreshold':2})
  self.v={'productId':'P1','orderId':'O1','purchasedQuantity':3,'demoPaymentApproved':True,'customerName':'Demo','customerEmail':'demo@example.com','demoPaymentApproved':True}
 def test_purchase_handoff_is_retry_safe_and_notifies(self):
  first=self.c.handle('1','commit-demo-order',self.v);self.assertTrue(first['orderAccepted'])
  self.assertEqual(first,self.c.handle('1','commit-demo-order',self.v))
  self.assertTrue(self.c.handle('2','commit-demo-order',self.v)['orderAccepted'])
  published=[]
  self.c.dispatch_outbox(lambda body:published.append(body) or {'messageKey':'1'},lambda body:{'id':body['id'],'accepted':True})
  self.assertEqual(1,len(published));self.assertEqual('f2-order-paid',published[0]['name'])
  self.c.handle('3','reduce-stock',published[0]['variables']);self.assertEqual(1,self.c.get('P1')['quantity'])
  self.c.handle('4','notify-low',self.v)
  self.assertEqual(1,self.c.db.execute('SELECT count(*) FROM notifications').fetchone()[0])
 def test_second_order_cannot_oversell(self):
  self.c.handle('1','commit-demo-order',self.v)
  result=self.c.handle('2','commit-demo-order',{**self.v,'orderId':'O2','purchasedQuantity':2})
  self.assertFalse(result['orderAccepted']);self.assertEqual(1,self.c.get('P1')['quantity'])
 def test_outside_season_invalid_unknown_and_declined_do_not_decrement(self):
  for i,changes in enumerate([{'demoPaymentApproved':False},{'purchasedQuantity':0},{'purchasedQuantity':1.5},{'productId':'missing'},{'customerEmail':''},{'demoPaymentApproved':False}]):
   result=self.c.handle(str(i),'commit-demo-order',{**self.v,**changes})
   self.assertFalse(result['orderAccepted'])
  self.assertFalse(self.c.handle('season','commit-demo-order',self.v,today=date(2100,1,1))['orderAccepted'])
  self.assertEqual(4,self.c.get('P1')['quantity'])
if __name__=='__main__':unittest.main()

