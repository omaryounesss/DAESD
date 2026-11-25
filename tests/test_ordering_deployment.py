"""A fresh deployment must resolve every dependency of the ordering diagram."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'services/inventory-service'))
spec = importlib.util.spec_from_file_location('deploy_ordering', ROOT / 'scripts/deploy_ordering.py')
deploy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deploy)
NS = {'b': 'http://www.omg.org/spec/BPMN/20100524/MODEL', 'z': 'http://camunda.org/schema/zeebe/1.0'}


class OrderingDeploymentTests(unittest.TestCase):
    def test_fresh_deployment_resolves_all_forms_and_called_processes(self):
        files = deploy.deployment_files()
        forms = {json.loads(p.read_text(encoding='utf-8'))['id'] for p in files if p.suffix == '.form'}
        roots = [ET.parse(p) for p in files if p.suffix == '.bpmn']
        processes = [p.get('id') for r in roots for p in r.findall('.//b:process', NS)]
        self.assertEqual(len(processes), len(set(processes)))
        self.assertIn('f2_customer_ordering', processes)
        for root in roots:
            for form in root.findall('.//z:formDefinition', NS):
                self.assertIn(form.get('formId'), forms)
            for child in root.findall('.//z:calledElement', NS):
                self.assertIn(child.get('processId'), processes)
        boundary, body = deploy.deployment_body()
        for p in files:
            self.assertIn(p.read_bytes(), body)
        self.assertTrue(body.endswith(('--' + boundary + '--\r\n').encode()))

    def test_ordering_alias_matches_canonical_horizontal_diagram(self):
        folder = ROOT / 'camunda/f2/processes'
        self.assertEqual((folder / 'place-order-horizontal.bpmn').read_bytes(),
                         (folder / 'place-order.bpmn').read_bytes())
