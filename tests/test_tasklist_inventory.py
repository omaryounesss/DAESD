import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('tasklist_worker',ROOT/'services/inventory-service/worker.py')
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)

class TasklistTests(unittest.TestCase):
    def test_preparation_reads_catalogue_and_generates_retry_stable_update_id(self):
        c=w.Catalogue(':memory:')
        c.seed({'productId':'P1','name':'Carrots','quantity':7,'availableFrom':'2026-11-01','availableUntil':'2026-12-31'})
        before=c.get('P1')
        v=c.handle('prepare-1','prepare-update',{'correctionAttempts':99,'updateId':'untrusted'})
        self.assertEqual(0,v['correctionAttempts'])
        self.assertTrue(v['updateId'].startswith('UI-'))
        self.assertEqual('P1',v['productOptions'][0]['value'])
        self.assertIn('Carrots',v['productOptions'][0]['label'])
        self.assertEqual(v,c.handle('prepare-1','prepare-update',{}))
        self.assertNotEqual(v['updateId'],c.handle('prepare-2','prepare-update',{})['updateId'])
        self.assertEqual(before,c.get('P1'))

    def test_empty_catalogue_does_not_seed_or_offer_a_fake_product(self):
        c=w.Catalogue(':memory:')
        self.assertEqual([],c.handle('prepare','prepare-update',{})['productOptions'])
        self.assertEqual(0,c.db.execute('SELECT count(*) FROM products').fetchone()[0])

if __name__=='__main__':unittest.main()

