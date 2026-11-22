import importlib.util
from pathlib import Path
import unittest
from datetime import date
import xml.etree.ElementTree as E

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('worker',ROOT/'services/inventory-service/worker.py')
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)
B='{http://www.omg.org/spec/BPMN/20100524/MODEL}'
Z='{http://camunda.org/schema/zeebe/1.0}'

class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.c=w.Catalogue(':memory:');self.day=date(2026,6,15)
        self.c.seed({'productId':'P1','quantity':10,'availableFrom':'2026-06-01','availableUntil':'2026-06-30','lowStockThreshold':5})
    def h(self,key,kind,**v):return self.c.handle(key,kind,{'productId':'P1',**v},self.day)
    def test_update_and_availability(self):
        self.assertTrue(self.h('a','save-update',quantity=20,availableFrom='2026-06-01',availableUntil='2026-06-30')['available'])
        self.assertFalse(self.h('b','save-update',quantity=20,availableFrom='2026-07-01',availableUntil='2026-07-30')['available'])
    def test_zero_then_restock(self):
        self.assertFalse(self.h('a','save-update',quantity=0,availableFrom='2026-06-01',availableUntil='2026-06-30')['available'])
        self.assertTrue(self.h('b','save-update',quantity=2,availableFrom='2026-06-01',availableUntil='2026-06-30')['available'])
    def test_invalid_update_count_and_correction(self):
        v={'productId':'P1','updateId':'U1','quantity':-1,'availableFrom':'bad','availableUntil':'bad'}
        for n in range(3):
            v.update(self.c.handle('q'+str(n),'validate-quantity',v,self.day))
            v.update(self.c.handle('s'+str(n),'validate-season',v,self.day))
        self.assertEqual(3,v['correctionAttempts']);self.assertFalse(v['updateValid'])
        self.assertEqual(10,self.c.get('P1')['quantity'])
        v.update(quantity=5,availableFrom='2026-06-01',availableUntil='2026-06-30')
        v.update(self.c.handle('q4','validate-quantity',v,self.day));v.update(self.c.handle('s4','validate-season',v,self.day))
        self.assertTrue(v['updateValid'])
    def test_job_and_order_idempotency(self):
        a=self.h('a','reduce-stock',orderId='O1',purchasedQuantity=7)
        self.assertEqual(a,self.h('a','reduce-stock',orderId='O1',purchasedQuantity=7))
        self.assertEqual(3,self.h('b','reduce-stock',orderId='O1',purchasedQuantity=7)['quantity'])
        with self.assertRaises(ValueError):self.h('c','reduce-stock',orderId='O1',purchasedQuantity=1)
    def test_oversell_rejected_without_mutation(self):
        with self.assertRaises(ValueError):self.h('a','reduce-stock',orderId='O1',purchasedQuantity=11)
        self.assertEqual(10,self.c.get('P1')['quantity'])
    def test_low_stock_and_zero_notifications_do_not_overlap(self):
        self.h('a','reduce-stock',orderId='O1',purchasedQuantity=8)
        self.h('b','notify-low');self.h('c','notify-low')
        self.assertEqual(1,self.c.db.execute('SELECT count(*) FROM notifications').fetchone()[0])
        self.h('d','reduce-stock',orderId='O2',purchasedQuantity=2)
        self.h('e','notify-zero');self.h('f','notify-low')
        self.assertEqual(2,self.c.db.execute('SELECT count(*) FROM notifications').fetchone()[0])
    def test_season_boundaries_inclusive_and_missed_end(self):
        for day,expected in [(date(2026,6,1),True),(date(2026,6,30),True),(date(2026,7,1),False)]:
            self.assertEqual(expected,self.c.handle(str(day),'retrieve-stock',{'productId':'P1'},day)['available'])
        self.assertEqual(1,len(self.c.handle('scan','scan-end',{},date(2026,7,2))['dueProducts']))
    def test_stale_timer_cannot_enable_out_of_season_product(self):
        self.h('a','save-update',quantity=10,availableFrom='2026-07-01',availableUntil='2026-07-30')
        self.assertFalse(self.h('b','available',seasonProduct={'productId':'P1','revision':1})['available'])
    def test_correction_outbox_is_durable_and_deduplicated(self):
        self.h('a','request-correction',updateId='U1',validationErrors=['Invalid'])
        self.h('a','request-correction',updateId='U1')
        self.assertEqual(1,self.c.db.execute('SELECT count(*) FROM outbox').fetchone()[0])
    def test_invalid_save_is_defended(self):
        with self.assertRaises(ValueError):self.h('a','save-update',quantity=-1,availableFrom='2026-06-01',availableUntil='2026-06-30')
        self.assertEqual(10,self.c.get('P1')['quantity'])

class ModelTests(unittest.TestCase):
    def test_original_nodes_and_flow_endpoints_preserved(self):
        src=E.parse(ROOT/'models/operational-bpmn/functionality-2/inventory-seasonal-availability.bpmn')
        dst=E.parse(ROOT/'camunda/f2/processes/inventory-seasonal-availability.bpmn')
        orig={e.get('id'):e for e in src.iter() if e.get('id')}
        new={e.get('id'):e for e in dst.iter() if e.get('id')}
        self.assertFalse(set(orig)-set(new))
        for key,e in orig.items():
            if e.tag==B+'sequenceFlow' and key not in ('Flow_0ccb63r','Flow_1klohxp'):
                self.assertEqual((e.get('sourceRef'),e.get('targetRef')),(new[key].get('sourceRef'),new[key].get('targetRef')))
    def test_executable_contracts_and_all_gateway_routes(self):
        for path in (ROOT/'camunda/f2/processes').glob('*.bpmn'):
            root=E.parse(path)
            for e in root.iter():
                if e.tag in (B+'serviceTask',B+'sendTask'):self.assertIsNotNone(e.find('.//'+Z+'taskDefinition'))
                if e.tag==B+'exclusiveGateway' and len(e.findall(B+'outgoing'))>1:
                    self.assertIsNotNone(e.get('default'))
                if e.tag==B+'timerEventDefinition':self.assertGreater(len(e),0)
                if e.tag==B+'messageEventDefinition':self.assertIsNotNone(e.get('messageRef'))
            for scope in root.iter():
                if scope.tag not in (B+'process',B+'subProcess'):continue
                nodes={e.get('id'):e for e in scope if e.get('id')}
                for flow in scope.findall(B+'sequenceFlow'):
                    self.assertIn(flow.get('id'),[e.text for e in nodes[flow.get('sourceRef')].findall(B+'outgoing')])
                    self.assertIn(flow.get('id'),[e.text for e in nodes[flow.get('targetRef')].findall(B+'incoming')])
    def test_admin_deadline_and_called_process(self):
        root=E.parse(ROOT/'camunda/f2/processes/inventory-seasonal-availability.bpmn')
        self.assertEqual('PT48H',root.find('.//'+B+'timeDuration').text)
        self.assertEqual('check_product_stock_status',root.find('.//'+Z+'calledElement').get('processId'))

if __name__=='__main__':unittest.main(verbosity=2)
