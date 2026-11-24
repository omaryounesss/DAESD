import importlib.util
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as E
from datetime import date
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('shared_worker',ROOT/'services/inventory-service/worker.py')
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)

class IntegrationTests(unittest.TestCase):
    def variables(self):
        return {'listingId':'LST-test','productId':'P2','productDetailsValid':True,
            'product':{'listingId':'LST-test','name':'Carrots','quantity':40,
                'availableFrom':'2026-11-01','availableUntil':'2026-12-31'},
            'traceabilityRecord':{'origin':'Bristol','allergens':'None'}}
    def test_publish_restart_update_purchase_and_retry(self):
        with tempfile.TemporaryDirectory() as temp:
            path=str(Path(temp)/'catalogue.sqlite3')
            c=w.Catalogue(path)
            result=c.handle('publish-1','publish-product',self.variables(),date(2026,11,24))
            self.assertEqual('P2',result['productId'])
            self.assertTrue(result['cataloguePersisted'])
            c.db.close()
            c=w.Catalogue(path)
            v={'productId':'P2','updateId':'U2','quantity':30,
               'availableFrom':'2026-11-01','availableUntil':'2026-12-31'}
            v.update(c.handle('q','validate-quantity',v))
            v.update(c.handle('s','validate-season',v))
            self.assertTrue(v['updateValid'])
            c.handle('update','save-update',v)
            c.handle('buy','reduce-stock',{'productId':'P2','orderId':'O1','purchasedQuantity':3})
            self.assertEqual(result,c.handle('publish-1','publish-product',self.variables()))
            c.handle('publish-2','publish-product',self.variables())
            self.assertEqual(27,c.get('P2')['quantity'])
            self.assertEqual(2,c.db.execute('SELECT count(*) FROM season_schedule').fetchone()[0])
            c.db.close()
    def test_auto_product_id_matches_listing(self):
        c=w.Catalogue(':memory:');v=self.variables();v.pop('productId')
        self.assertEqual('LST-test',c.handle('p','publish-product',v)['productId'])
    def test_invalid_publications_leave_no_product_or_cached_job(self):
        for change in ({'productDetailsValid':False},{'traceabilityRecord':{}},
                       {'listingId':'different'},
                       {'product':{'listingId':'LST-test','quantity':-1}}):
            c=w.Catalogue(':memory:');v=self.variables();v.update(change)
            with self.assertRaises((ValueError,KeyError)):c.handle('p','publish-product',v)
            self.assertEqual(0,c.db.execute('SELECT count(*) FROM products').fetchone()[0])
            self.assertEqual(0,c.db.execute('SELECT count(*) FROM jobs').fetchone()[0])
    def test_id_collision_does_not_overwrite(self):
        c=w.Catalogue(':memory:')
        c.seed({'productId':'P2','quantity':7,'availableFrom':'2026-11-01','availableUntil':'2026-12-31'})
        with self.assertRaises(ValueError):c.handle('p','publish-product',self.variables())
        self.assertEqual(7,c.get('P2')['quantity'])
    def test_process_persists_before_success_notification(self):
        ns={'b':'http://www.omg.org/spec/BPMN/20100524/MODEL',
            'z':'http://camunda.org/schema/zeebe/1.0'}
        root=E.parse(ROOT/'camunda/f1/processes/product-listing-publication.bpmn')
        task=root.find(".//b:serviceTask[@id='Task_PublishListing']",ns)
        self.assertEqual('f1-publish-product',task.find('b:extensionElements/z:taskDefinition',ns).get('type'))
        flow=root.find(".//b:sequenceFlow[@sourceRef='Task_PublishListing']",ns)
        self.assertEqual('Task_NotifyPublished',flow.get('targetRef'))
if __name__=='__main__':unittest.main()

