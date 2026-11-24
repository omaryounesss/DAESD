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
    def test_season_boundaries_are_inclusive(self):
        for day,expected in [(date(2026,6,1),True),(date(2026,6,30),True),(date(2026,7,1),False)]:
            self.assertEqual(expected,self.c.handle(str(day),'retrieve-stock',{'productId':'P1'},day)['available'])

    def test_stale_timer_cannot_enable_out_of_season_product(self):
        self.h('a','save-update',quantity=10,availableFrom='2026-07-01',availableUntil='2026-07-30')
        self.assertFalse(self.h('b','available')['available'])
    def test_original_timer_route_uses_explicit_demo_product(self):
        from unittest.mock import patch
        with patch.dict(w.os.environ,{'F2_TIMER_PRODUCT_ID':'P1'}):
            self.assertEqual('P1',self.c.handle('timer','retrieve-stock',{},self.day)['productId'])
    def test_correction_request_is_recorded_once(self):
        self.h('a','request-correction',updateId='U1',validationErrors=['Invalid'])
        self.h('a','request-correction',updateId='U1')
        self.assertEqual(1,self.c.db.execute('SELECT count(*) FROM notifications').fetchone()[0])
    def test_invalid_save_is_defended(self):
        with self.assertRaises(ValueError):self.h('a','save-update',quantity=-1,availableFrom='2026-06-01',availableUntil='2026-06-30')
        self.assertEqual(10,self.c.get('P1')['quantity'])

class ModelTests(unittest.TestCase):
    def test_documented_tasklist_refinements_preserve_business_routes(self):
        src=E.parse(ROOT/'models/operational-bpmn/functionality-2/inventory-seasonal-availability.bpmn')
        dst=E.parse(ROOT/'camunda/f2/processes/inventory-seasonal-availability.bpmn')
        orig={e.get('id'):e for e in src.iter() if e.get('id')}
        new={e.get('id'):e for e in dst.iter() if e.get('id')}
        self.assertEqual({'MessageEventDefinition_0b0n9pd'},set(orig)-set(new))
        for key,e in orig.items():
            if e.tag==B+'sequenceFlow':
                self.assertEqual((e.get('sourceRef'),e.get('targetRef')),(new[key].get('sourceRef'),new[key].get('targetRef')))
        added=set(new)-set(orig)
        business_added={k for k in added if new[k].tag in (B+'task',B+'userTask',B+'serviceTask',B+'startEvent',B+'endEvent',B+'subProcess',B+'sequenceFlow')}
        self.assertEqual({'Start_ProducerUpdate','Task_PrepareProducerUpdate','Task_SubmitStockUpdate',
                         'Flow_ProducerPrepare','Flow_ProducerSubmit','Flow_ProducerValidate'},business_added)
        self.assertEqual(B+'userTask',new['Event_0pab392'].tag)
        def ownership(t):
            return {c.get('id'):e.get('id') for e in t.iter() for c in e if c.get('id') in orig and c.get('id')!='MessageEventDefinition_0b0n9pd'}
        self.assertEqual(ownership(src),ownership(dst))

    def test_tasklist_forms_limit_outputs_and_leave_paid_order_start(self):
        import json
        root=E.parse(ROOT/'camunda/f2/processes/inventory-seasonal-availability.bpmn')
        for ident,fid,outputs in [('Task_SubmitStockUpdate','f2-stock-update',{'productId','quantity','availableFrom','availableUntil'}),
                                  ('Event_0pab392','f2-stock-correction',{'quantity','availableFrom','availableUntil'})]:
            task=root.find(".//"+B+"userTask[@id='"+ident+"']")
            self.assertIsNotNone(task.find('.//'+Z+'userTask'))
            self.assertEqual(fid,task.find('.//'+Z+'formDefinition').get('formId'))
            self.assertEqual(outputs,{e.get('target') for e in task.findall('.//'+Z+'output')})
            form=json.loads((ROOT/'camunda/f2/forms'/ (fid+'.form')).read_text())
            self.assertEqual(outputs,{c['key'] for c in form['components'] if 'key' in c})
        self.assertIsNotNone(root.find(".//"+B+"startEvent[@id='Start_ProducerUpdate']"))
        self.assertIsNotNone(root.find(".//"+B+"startEvent[@id='Event_0k7qpmm']/"+B+'messageEventDefinition'))
        self.assertEqual(3,len(root.findall('.//'+B+'userTask')))

    def test_external_labels_move_with_their_original_geometry(self):
        d='{http://www.omg.org/spec/BPMN/20100524/DI}'
        c='{http://www.omg.org/spec/DD/20100524/DC}'
        src=E.parse(ROOT/'models/operational-bpmn/functionality-2/inventory-seasonal-availability.bpmn')
        dst=E.parse(ROOT/'camunda/f2/processes/inventory-seasonal-availability.bpmn')
        elements={e.get('bpmnElement'):e for e in dst.iter() if e.get('bpmnElement')}
        checked=0
        for original in src.iter():
            label=original.find(d+'BPMNLabel/'+c+'Bounds')
            if label is None:continue
            ident=original.get('bpmnElement')
            if ident=='Event_0pab392':
                self.assertIsNone(elements[ident].find(d+'BPMNLabel'))
                continue
            actual=elements[ident].find(d+'BPMNLabel/'+c+'Bounds')
            self.assertIsNotNone(actual,ident)
            old_y=float(label.get('y'))
            self.assertEqual(old_y+(180 if old_y>=430 else 0),float(actual.get('y')),ident)
            self.assertEqual(float(label.get('x')),float(actual.get('x')),ident)
            checked+=1
        self.assertGreater(checked,10)

    def test_responsibility_lanes_and_correction_edges_match_task_geometry(self):
        d='{http://www.omg.org/spec/BPMN/20100524/DI}'
        dc='{http://www.omg.org/spec/DD/20100524/DC}'
        di='{http://www.omg.org/spec/DD/20100524/DI}'
        r=E.parse(ROOT/'camunda/f2/processes/inventory-seasonal-availability.bpmn')
        lanes={lane.get('id'):{ref.text for ref in lane.findall(B+'flowNodeRef')} for lane in r.findall('.//'+B+'lane')}
        self.assertIn('Event_0pab392',lanes['Lane_ProducerTasklist'])
        self.assertNotIn('Event_0pab392',lanes['Lane_1w7vtzs'])
        self.assertIn('Task_PrepareProducerUpdate',lanes['Lane_1w7vtzs'])
        self.assertNotIn('Task_PrepareProducerUpdate',lanes['Lane_ProducerTasklist'])
        edge=r.find('.//'+d+"BPMNEdge[@bpmnElement='Flow_12vo3s4']")
        points=[(float(p.get('x')),float(p.get('y'))) for p in edge.findall(di+'waypoint')]
        shape=r.find('.//'+d+"BPMNShape[@bpmnElement='Event_0pab392']/"+dc+'Bounds')
        self.assertEqual(float(shape.get('y'))+float(shape.get('height')),points[0][1])
        self.assertGreater(points[1][1],points[0][1])
        self.assertTrue(all(a[0]==b[0] or a[1]==b[1] for a,b in zip(points,points[1:])))

    def test_seasonal_starts_use_messages_without_fixed_dates(self):
        r=E.parse(ROOT/'camunda/f2/processes/inventory-seasonal-availability.bpmn')
        self.assertEqual([],r.findall('.//'+B+'timeDate'))
        for ident,name in [('Event_0ii4tpz','f2-season-start'),('Event_0g3ep4s','f2-season-end')]:
            event=r.find('.//'+B+"startEvent[@id='"+ident+"']")
            definition=event.find(B+'messageEventDefinition')
            self.assertIsNotNone(definition)
            self.assertEqual(name,r.find('.//'+B+"message[@id='"+definition.get('messageRef')+"']").get('name'))
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

