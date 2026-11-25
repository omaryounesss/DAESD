import importlib.util
from pathlib import Path
import unittest
import json

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('tasklist_worker',ROOT/'services/inventory-service/worker.py')
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)

class TasklistTests(unittest.TestCase):
    def test_date_form_values_follow_existing_validation_and_persistence_contract(self):
        c=w.Catalogue(':memory:')
        c.seed({'productId':'P1','name':'Carrots','quantity':7,'availableFrom':'2026-11-01','availableUntil':'2026-12-31'})
        for fid in ('f2-stock-update','f2-stock-correction'):
            path=ROOT/'camunda/f2/forms'/f'{fid}.form'
            self.assertEqual(path.read_bytes(),(ROOT/'source/forms'/path.name).read_bytes())
            obj=json.loads(path.read_text())
            fields={f['key']:f for f in obj['components'] if 'key' in f}
            for key in ('availableFrom','availableUntil'):
                self.assertEqual(('datetime','date'),(fields[key]['type'],fields[key]['subtype']))
                self.assertTrue(fields[key]['validate']['required'])
            # Date-only form values use the same ISO contract as existing F1.
            values={'productId':'P1','updateId':fid,'quantity':3,
                    'availableFrom':'2026-11-25','availableUntil':'2026-12-31'}
            values.update(c.handle(fid+'-quantity','validate-quantity',values))
            invalid={**values,'availableUntil':'2026-11-01'}
            self.assertFalse(c.handle(fid+'-invalid','validate-season',invalid)['updateValid'])
            values.update(c.handle(fid+'-season','validate-season',values))
            self.assertTrue(values['updateValid'])
            c.handle(fid+'-save','save-update',values)
            self.assertEqual('2026-11-25',c.get('P1')['availableFrom'])
            self.assertEqual('2026-12-31',c.get('P1')['availableUntil'])

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

