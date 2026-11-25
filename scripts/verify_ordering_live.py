"""Rehearse native ordering against synthetic stock; requires the shared worker running.

Does not start workers, change real products, or use real payments. Each invocation
uses a new product and preserves its instances and receipts for inspection.
"""
import argparse
from datetime import date, timedelta
import json
from pathlib import Path
import sqlite3
import sys
import time
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parents[1]
SERVICE = ROOT / 'services/inventory-service'
sys.path.insert(0, str(SERVICE))
import connect_f2
import worker


def until(check, description, timeout):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        result = check()
        if result:
            return result
        time.sleep(2)
    raise TimeoutError(description)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--credentials', type=Path, required=True)
    parser.add_argument('--db', type=Path, default=SERVICE / 'f2-catalogue.sqlite3')
    parser.add_argument('--report', type=Path, default=ROOT / 'docs/ordering-live-verification.json')
    parser.add_argument('--timeout', type=int, default=150)
    args = parser.parse_args()
    if not args.db.is_file():
        raise ValueError('Use the existing database of the running shared worker')
    # Check local services before creating any product or process instance.
    for port, service in [(8765, 'daesd-notification-simulation'), (8766, 'daesd-payment-simulation')]:
        with urllib.request.urlopen(f'http://127.0.0.1:{port}/health', timeout=3) as response:
            if json.loads(response.read()).get('service') != service:
                raise ValueError(f'Expected simulation is not running on port {port}')
    connect_f2.load_credentials(args.credentials)
    worker.os.environ.setdefault('CAMUNDA_REST_ADDRESS', connect_f2.ENDPOINT)
    if worker.setting('CAMUNDA_REST_ADDRESS', 'ZEEBE_REST_ADDRESS').rstrip('/').removesuffix('/v2') != connect_f2.ENDPOINT:
        raise ValueError('Unexpected cluster')
    worker.request('/topology')
    stamp = uuid.uuid4().hex[:12]
    pid = 'ORDER-VERIFY-' + stamp
    report = {'status': 'RUNNING', 'productId': pid, 'cases': [], 'simulation': True}

    def save():
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2), encoding='utf-8')

    def task(key, ids):
        def find():
            items = worker.request('/user-tasks/search', {'filter': {'processInstanceKey': str(key), 'state': 'CREATED'}, 'page': {'limit': 100}}).get('items', [])
            return next((item for item in items if item.get('elementId') in ids), None)
        return until(find, 'No expected native task for ' + str(key), args.timeout)

    def complete(item, variables):
        key = str(item['userTaskKey'])
        if not worker.request('/user-tasks/' + key + '/form'):
            raise ValueError('Native task has no resolvable deployed form')
        worker.request('/user-tasks/' + key + '/completion', {'variables': variables})

    catalogue = worker.Catalogue(str(args.db))
    try:
        catalogue.seed({'productId': pid, 'name': 'Synthetic ordering verification ' + stamp,
                        'quantity': 4, 'lowStockThreshold': 2,
                        'availableFrom': str(date.today() - timedelta(days=1)),
                        'availableUntil': str(date.today() + timedelta(days=7))})
        save()
        for label, quantity, outcome, accepted, stock in [
            ('success', 3, 'approve', True, 1),
            ('declined', 1, 'decline', False, 1),
            ('insufficient-stock', 2, 'approve', False, 1),
            ('last-item', 1, 'approve', True, 0),
        ]:
            instance = worker.request('/process-instances', {'processDefinitionId': 'f2_customer_ordering', 'variables': {'rehearsalId': stamp}})
            key = instance['processInstanceKey']
            case = {'case': label, 'processInstanceKey': str(key), 'requestedQuantity': quantity}
            report['cases'].append(case)
            save()
            complete(task(key, {'Order'}), {'productId': pid, 'purchasedQuantity': quantity,
                     'customerName': 'Synthetic test customer', 'customerEmail': 'test@example.com'})
            next_task = task(key, {'PayChoice', 'Reject'})
            if next_task['elementId'] == 'PayChoice':
                complete(next_task, {'demoPaymentOutcome': outcome})
                next_task = task(key, {'Result', 'Reject'})
            case['accepted'] = next_task['elementId'] == 'Result'
            case['stock'] = catalogue.get(pid)['quantity']
            if case['accepted'] != accepted or case['stock'] != stock:
                raise AssertionError('Unexpected ordering result: ' + label)
            complete(next_task, {})
            until(lambda: worker.request('/process-instances/' + str(key)).get('state') == 'COMPLETED',
                  'Instance did not complete: ' + str(key), args.timeout)
            case['state'] = 'COMPLETED'
            save()
            print(label + ': PASS', flush=True)

        receipts = args.db.with_name('notification-receipts.sqlite3')
        payments = args.db.with_name('payment-receipts.sqlite3')

        def notifications_received():
            if not receipts.is_file():
                return False
            with sqlite3.connect(receipts) as db:
                events = [json.loads(row[0]) for row in db.execute("SELECT event FROM receipts WHERE json_extract(event,'$.productId')=?", (pid,))]
            return events if {'low-stock', 'out-of-stock'} <= {event.get('type') for event in events} else False

        report['notificationReceipts'] = until(notifications_received, 'Missing low/zero-stock receipts', args.timeout)
        if not payments.is_file():
            raise AssertionError('Missing payment receipt database')
        with sqlite3.connect(payments) as db:
            rows = db.execute("SELECT id,status FROM payments WHERE json_extract(details,'$.productId')=?", (pid,)).fetchall()
        if sorted(status for _, status in rows) != ['captured', 'captured', 'declined']:
            raise AssertionError('Unexpected payment receipt outcomes')
        report['paymentReceipts'] = [{'orderId': ident, 'status': status} for ident, status in rows]
        report['status'] = 'PASS'
        save()
        print('PASS: four native instances, stock 4 -> 1 -> 1 -> 1 -> 0, payment and notification receipts.')
    except Exception as exc:
        report.update(status='FAILED', error=str(exc))
        save()
        raise
    finally:
        catalogue.db.close()


if __name__ == '__main__':
    main()
