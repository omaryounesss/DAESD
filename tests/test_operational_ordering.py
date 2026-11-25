import importlib.util,unittest,tempfile,xml.etree.ElementTree as E
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def module(name):
 spec=importlib.util.spec_from_file_location(name,ROOT/'services/inventory-service'/f'{name}.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
w=module('worker');pay=module('payment_service')
class PaymentFlowTests(unittest.TestCase):
 def test_service_lifecycle_and_conflicting_replays(self):
  with tempfile.TemporaryDirectory() as d:
   p=pay.Payments(str(Path(d)/'payments.db'));v={'orderId':'A','productId':'P1','purchasedQuantity':3,'demoPaymentOutcome':'approve','action':'authorize'}
   self.assertEqual('authorized',p.apply(v)['paymentStatus']);self.assertEqual('authorized',p.apply(v)['paymentStatus'])
   self.assertEqual('captured',p.apply({**v,'action':'capture'})['paymentStatus']);self.assertEqual('captured',p.apply({**v,'action':'capture'})['paymentStatus'])
   with self.assertRaises(ValueError):p.apply({**v,'action':'void'})
   with self.assertRaises(ValueError):p.apply({**v,'purchasedQuantity':4})
   self.assertEqual('declined',p.apply({**v,'orderId':'B','demoPaymentOutcome':'decline'})['paymentStatus'])
   p.db.close()
 def test_stock_race_voids_authorization_and_preserves_stock(self):
  with tempfile.TemporaryDirectory() as d:
   p=pay.Payments(str(Path(d)/'payments.db'));c=w.Catalogue(':memory:')
   c.seed({'productId':'P1','quantity':4,'availableFrom':'2026-01-01','availableUntil':'2099-12-31'})
   v={'orderId':'A','productId':'P1','purchasedQuantity':3,'customerName':'Test','customerEmail':'test@example.com','demoPaymentOutcome':'approve'}
   self.assertTrue(c.handle('validate','validate-order',v)['orderValid'])
   receipt=p.apply({**v,'action':'authorize'});c.handle('other','reduce-stock',{'productId':'P1','orderId':'other','purchasedQuantity':2})
   result=c.handle('commit','commit-order',{**v,**receipt});self.assertFalse(result['orderAccepted'])
   self.assertEqual('voided',p.apply({**v,'action':'void'})['paymentStatus']);self.assertEqual(2,c.get('P1')['quantity']);p.db.close();c.db.close()
 def test_direct_operational_route_does_not_launch_second_inventory_instance(self):
  c=w.Catalogue(':memory:');c.seed({'productId':'P1','quantity':4,'availableFrom':'2026-01-01','availableUntil':'2099-12-31'})
  v={'orderId':'A','productId':'P1','purchasedQuantity':3,'customerName':'Test','customerEmail':'test@example.com','paymentAuthorized':True}
  self.assertTrue(c.handle('commit','commit-order',v)['orderAccepted']);self.assertEqual(0,c.db.execute('SELECT count(*) FROM outbox').fetchone()[0]);c.handle('notify','notify-low',v)
  self.assertEqual(1,c.db.execute('SELECT count(*) FROM notifications').fetchone()[0])
 def test_operational_purchase_tasks_preserved_and_forms_bound(self):
  ns={'b':'http://www.omg.org/spec/BPMN/20100524/MODEL','z':'http://camunda.org/schema/zeebe/1.0'}
  root=E.parse(ROOT/'camunda/f2/processes/place-order.bpmn')
  for ident in ('Gateway_03r47f5','Gateway_0lj5e6t','Activity_0a0msio','Activity_1knv4gv','Activity_0kb95hx'):self.assertIsNotNone(root.find('.//*[@id="'+ident+'"]'))
  self.assertEqual(4,len(root.findall('.//b:participant',ns)))
  original=E.parse(ROOT/'camunda/f2/processes/inventory-seasonal-availability.bpmn')
  original_ids={e.get('id') for e in original.findall('.//b:process/*',ns) if e.get('id')}
  new_ids={e.get('id') for e in root.findall('.//b:process/*',ns) if e.get('id')}
  removed=original_ids-new_ids
  self.assertTrue(all(i.startswith('Flow_') for i in removed),removed)
  all_ids=[e.get('id') for e in root.iter() if e.get('id')]
  self.assertEqual(len(all_ids),len(set(all_ids)))
  for f in root.findall('.//z:formDefinition',ns):self.assertTrue((ROOT/'camunda/f2/forms'/(f.get('formId')+'.form')).exists())
