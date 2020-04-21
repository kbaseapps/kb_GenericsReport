# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os

from kb_GenericsReport.Utils.HeatmapUtil import HeatmapUtil
#END_HEADER


class kb_GenericsReport:
    '''
    Module Name:
    kb_GenericsReport

    Module Description:
    A KBase module: kb_GenericsReport
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "1.0.0"
    GIT_URL = "https://github.com/Tianhao-Gu/kb_GenericsReport.git"
    GIT_COMMIT_HASH = "e4039b10ee7d4fd23c6260481c345251dd932d97"

    #BEGIN_CLASS_HEADER
    @staticmethod
    def validate_params(params, expected, opt_param=set()):
        """Validates that required parameters are present. Warns if unexpected parameters appear"""
        expected = set(expected)
        opt_param = set(opt_param)
        pkeys = set(params)
        if expected - pkeys:
            raise ValueError("Required keys {} not in supplied parameters"
                             .format(", ".join(expected - pkeys)))
        defined_param = expected | opt_param
        for param in params:
            if param not in defined_param:
                logging.warning("Unexpected parameter {} supplied".format(param))
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.shared_folder = config['scratch']
        config['SDK_CALLBACK_URL'] = os.environ['SDK_CALLBACK_URL']
        config['KB_AUTH_TOKEN'] = os.environ['KB_AUTH_TOKEN']
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        self.heatmap_util = HeatmapUtil(config)
        #END_CONSTRUCTOR
        pass


    def build_heatmap_html(self, ctx, params):
        """
        :param params: instance of type "build_heatmap_html_params" (required
           params: tsv_file_path: matrix data in tsv format optional params:
           cluster_data: True if data should be clustered. Default: True
           dist_metric: distance metric used for clustering. Default:
           euclidean
           (https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial
           .distance.pdist.html) linkage_method: linkage method used for
           clustering. Default: ward
           (https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster
           .hierarchy.linkage.html)) -> structure: parameter "tsv_file_path"
           of String, parameter "cluster_data" of type "boolean" (A boolean -
           0 for false, 1 for true.), parameter "dist_metric" of String,
           parameter "linkage_method" of String
        :returns: instance of type "build_heatmap_html_result" -> structure:
           parameter "html_dir" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN build_heatmap_html
        self.validate_params(params, ['tsv_file_path'],
                             opt_param=['cluster_data', 'dist_metric', 'linkage_method'])
        output = self.heatmap_util.build_heatmap_html(params)
        #END build_heatmap_html

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method build_heatmap_html return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
