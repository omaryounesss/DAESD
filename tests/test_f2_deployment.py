import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('f2_deploy',ROOT/'scripts/deploy_f2.py')
deployment=importlib.util.module_from_spec(spec);spec.loader.exec_module(deployment)

class DeploymentTests(unittest.TestCase):
    def test_bound_forms_and_both_processes_are_in_one_deployment(self):
        boundary,body=deployment.deployment_body()
        self.assertEqual(5,body.count(b'name="resources"'))
        for filename in ['inventory-seasonal-availability.bpmn','check-product-stock-status.bpmn',
                         'f2-stock-update.form','f2-stock-correction.form','f2-inventory-review.form']:
            self.assertIn(('filename="'+filename+'"').encode(),body)
        self.assertTrue(body.endswith(('--'+boundary+'--\r\n').encode()))
        self.assertNotIn(b'<bpmn:timeDate>',body)

if __name__=='__main__':unittest.main()

