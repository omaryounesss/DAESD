import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SERVICE=Path(__file__).resolve().parents[1]/'services/inventory-service'
spec=importlib.util.spec_from_file_location('connection_worker',SERVICE/'worker.py')
w=importlib.util.module_from_spec(spec);spec.loader.exec_module(w)

class Response:
    def __init__(self,body):self.body=body
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def read(self):return json.dumps(self.body).encode()

class ConnectionTests(unittest.TestCase):
    def setUp(self):w._oauth_token=None;w._oauth_expires=0
    def test_oauth_aliases_cache_and_expiry(self):
        env={'ZEEBE_CLIENT_ID':'example-client','ZEEBE_CLIENT_SECRET':'example-secret'}
        with patch.dict(os.environ,env,clear=True),patch.object(w.time,'monotonic',side_effect=[100,120,200,200]),patch.object(w.urllib.request,'urlopen',side_effect=[Response({'access_token':'first','expires_in':100}),Response({'access_token':'second','expires_in':100})]) as transport:
            self.assertEqual('Bearer first',w.authorization_header())
            self.assertEqual('Bearer first',w.authorization_header())
            self.assertEqual('Bearer second',w.authorization_header())
            self.assertEqual(2,transport.call_count)
            payload=transport.call_args_list[0].args[0].data.decode()
            self.assertIn('grant_type=client_credentials',payload)
    def test_non_https_oauth_endpoint_rejected(self):
        with patch.dict(os.environ,{'CAMUNDA_CLIENT_ID':'id','CAMUNDA_CLIENT_SECRET':'secret','CAMUNDA_OAUTH_URL':'http://insecure.invalid/token'},clear=True):
            with self.assertRaises(ValueError):w.authorization_header()
    def test_rest_path_alias_and_get_request(self):
        with patch.dict(os.environ,{'ZEEBE_REST_ADDRESS':'https://example.invalid/cluster/v2','CAMUNDA_ACCESS_TOKEN':'example'},clear=True),patch.object(w.urllib.request,'urlopen',return_value=Response({'brokers':[]})) as transport:
            w.request('/topology')
            req=transport.call_args.args[0]
            self.assertEqual('https://example.invalid/cluster/v2/topology',req.full_url)
            self.assertEqual('GET',req.get_method())
            self.assertEqual('Bearer example',req.get_header('Authorization'))
    def test_env_file_is_parsed_as_data_and_ignores_unrelated_keys(self):
        with patch.dict(sys.modules,{'worker':w}):
            module=importlib.util.spec_from_file_location('connector',SERVICE/'connect_f2.py')
            c=importlib.util.module_from_spec(module);module.loader.exec_module(c)
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'example.env'
            p.write_text('export ZEEBE_CLIENT_ID="example"\nZEEBE_CLIENT_SECRET=literal$(never-execute)\nUNRELATED=value\n')
            with patch.dict(os.environ,{},clear=True):
                c.load_credentials(p)
                self.assertEqual('example',os.environ['ZEEBE_CLIENT_ID'])
                self.assertEqual('literal$(never-execute)',os.environ['ZEEBE_CLIENT_SECRET'])
                self.assertNotIn('UNRELATED',os.environ)

    def test_springboot_credentials_and_cluster_check(self):
        with patch.dict(sys.modules,{'worker':w}):
            module=importlib.util.spec_from_file_location('connector_properties',SERVICE/'connect_f2.py')
            c=importlib.util.module_from_spec(module);module.loader.exec_module(c)
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/'example.properties'
            p.write_text('camunda.client.auth.client-id=example\ncamunda.client.auth.client-secret=example-secret\ncamunda.client.cloud.cluster-id=848240b1-573c-4a07-bd52-723bea5b23b7\n')
            with patch.dict(os.environ,{},clear=True):
                c.load_credentials(p)
                self.assertEqual('example',os.environ['CAMUNDA_CLIENT_ID'])
                self.assertEqual('example-secret',os.environ['CAMUNDA_CLIENT_SECRET'])
                p.write_text('camunda.client.cloud.cluster-id=different-cluster\n')
                with self.assertRaises(ValueError):c.load_credentials(p)

if __name__=='__main__':unittest.main(verbosity=2)

