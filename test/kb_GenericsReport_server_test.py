# -*- coding: utf-8 -*-
import os
import time
import unittest
from configparser import ConfigParser

from kb_GenericsReport.kb_GenericsReportImpl import kb_GenericsReport
from kb_GenericsReport.kb_GenericsReportServer import MethodContext
from kb_GenericsReport.authclient import KBaseAuth as _KBaseAuth

from installed_clients.WorkspaceClient import Workspace


class kb_GenericsReportTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = os.environ.get('KB_AUTH_TOKEN', None)
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('kb_GenericsReport'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'kb_GenericsReport',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = Workspace(cls.wsURL)
        cls.serviceImpl = kb_GenericsReport(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        suffix = int(time.time() * 1000)
        cls.wsName = "test_ContigFilter_" + str(suffix)
        ret = cls.wsClient.create_workspace({'workspace': cls.wsName})  # noqa

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def test_bad_params(self):
        with self.assertRaises(ValueError) as context:
            self.serviceImpl.build_heatmap_html(self.ctx, {'workspace_name': self.wsName})
            self.assertIn("Required keys", str(context.exception.args))

    def test_build_heatmap_html(self):
        params = {'tsv_file_path': os.path.join('data', 'amplicon_test.tsv')}
        returnVal = self.serviceImpl.build_heatmap_html(self.ctx, params)[0]

        self.assertIn('html_dir', returnVal)

        html_dir = returnVal.get('html_dir')
        html_report_files = os.listdir(html_dir)

        self.assertEqual(2, len(html_report_files))
