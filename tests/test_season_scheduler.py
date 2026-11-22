import importlib.util
from pathlib import Path
from datetime import datetime, date, timezone
import json
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('inventory_worker',ROOT/'services/inventory-service/worker.py')
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)

def instant(day):return datetime.fromisoformat(day+'T00:00:00+00:00')

class SchedulerTests(unittest.TestCase):
    def setUp(self):
        self.c=w.Catalogue(':memory:')
        self.product={'productId':'P1','quantity':10,'availableFrom':'2027-06-01','availableUntil':'2027-06-30'}
        self.c.seed(self.product)
    def update(self,key,**changes):
        p=self.c.get('P1')
        return self.c.handle(key,'save-update',{'productId':'P1','quantity':p['quantity'],
            'availableFrom':p['availableFrom'],'availableUntil':p['availableUntil'],**changes},date(2027,5,1))
    def test_changed_dates_cancel_old_start_and_end(self):
        self.update('change',availableFrom='2027-07-01',availableUntil='2027-07-31')
        self.assertEqual(2,self.c.db.execute("SELECT count(*) FROM season_schedule WHERE status='cancelled'").fetchone()[0])
        self.assertEqual([],self.c.apply_due_seasons(instant('2027-06-01')))
        self.assertEqual([],self.c.apply_due_seasons(instant('2027-07-01')-w.timedelta(seconds=1)))
        events=self.c.apply_due_seasons(instant('2027-07-01'))
        self.assertEqual(1,len(events));self.assertTrue(self.c.get('P1')['available'])
        self.assertEqual([],self.c.apply_due_seasons(instant('2027-07-31')))
        self.c.apply_due_seasons(instant('2027-08-01'))
        self.assertFalse(self.c.get('P1')['available'])
    def test_zero_stock_at_start_stays_unavailable(self):
        self.update('zero',quantity=0)
        self.c.apply_due_seasons(instant('2027-06-01'))
        self.assertFalse(self.c.get('P1')['available'])
    def test_order_uses_latest_stock_without_cancelling_schedule(self):
        self.c.handle('sale','reduce-stock',{'productId':'P1','orderId':'O1','purchasedQuantity':10},date(2027,5,31))
        self.assertEqual(1,self.c.get('P1')['seasonVersion'])
        self.c.apply_due_seasons(instant('2027-06-01'))
        self.assertFalse(self.c.get('P1')['available'])
    def test_restart_recovers_missed_boundaries_and_does_not_replay(self):
        with tempfile.TemporaryDirectory() as directory:
            path=str(Path(directory)/'catalogue.sqlite3')
            c=w.Catalogue(path);c.seed(self.product);c.db.close()
            c=w.Catalogue(path)
            actions=c.apply_due_seasons(instant('2027-07-05'))
            self.assertEqual(2,len(actions));self.assertTrue(all(not a['available'] for a in actions))
            c.db.close();c=w.Catalogue(path)
            self.assertEqual([],c.apply_due_seasons(instant('2027-07-05')))
            self.assertEqual(2,c.db.execute('SELECT count(*) FROM season_events').fetchone()[0]);c.db.close()
    def test_multiple_products_have_independent_schedules(self):
        self.c.seed({**self.product,'productId':'P2','availableFrom':'2027-07-01','availableUntil':'2027-07-31'})
        actions=self.c.apply_due_seasons(instant('2027-06-01'))
        self.assertEqual(['P1'],[a['productId'] for a in actions])
        self.assertFalse(self.c.get('P2')['available'])
    def test_invalid_update_does_not_cancel_valid_schedule(self):
        before=self.c.db.execute('SELECT * FROM season_schedule').fetchall()
        with self.assertRaises(ValueError):self.update('invalid',availableUntil='2027-01-01')
        self.assertEqual(before,self.c.db.execute('SELECT * FROM season_schedule').fetchall())
    def test_retry_and_stock_only_update_do_not_replace_schedule(self):
        self.update('change',availableFrom='2027-07-01',availableUntil='2027-07-31')
        before=self.c.db.execute('SELECT * FROM season_schedule').fetchall()
        self.update('change',availableFrom='2027-07-01',availableUntil='2027-07-31')
        self.update('stock',quantity=8)
        self.assertEqual(before,self.c.db.execute('SELECT * FROM season_schedule').fetchall())
    def test_stale_pending_action_is_rejected_even_if_not_cancelled(self):
        self.update('change',availableFrom='2027-07-01',availableUntil='2027-07-31')
        self.c.db.execute("UPDATE season_schedule SET status='pending' WHERE season_version=1");self.c.db.commit()
        self.assertEqual([],self.c.apply_due_seasons(instant('2027-06-01')))
        self.assertFalse(self.c.get('P1')['available'])

if __name__=='__main__':unittest.main(verbosity=2)
