
import errno
import os
import logging
import pandas as pd
from xlrd.biffh import XLRDError
import uuid
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist
import json
import sys
from matplotlib import pyplot as plt

# from installed_clients.DataFileUtilClient import DataFileUtil


class HeatmapUtil:

    def _mkdir_p(self, path):
        """
        _mkdir_p: make directory for given path
        """
        if not path:
            return
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    def _compute_cluster_label_order(self, values, labels,
                                     dist_metric='euclidean',
                                     linkage_method='ward'):

        # values = [[1, 0, 21, 50, 1], [20, 0, 60, 80, 30], [30, 60, 1, -10, 20]]
        # labels = ['model_1', 'model_2', 'model_3']
        if len(labels) == 1:
            return labels
        dist_matrix = pdist(values, metric=dist_metric)
        linkage_matrix = linkage(dist_matrix, method=linkage_method)

        dn = dendrogram(linkage_matrix, labels=labels, distance_sort='ascending')

        ordered_label = dn['ivl']

        return ordered_label

    def _read_csv_file(self, file_path):
        logging.info('Start reading data file: {}'.format(file_path))

        try:
            df = pd.read_excel(file_path, dtype='str',  index_col=0)
        except XLRDError:
            reader = pd.read_csv(file_path, sep=None, iterator=True)
            inferred_sep = reader._engine.data.dialect.delimiter
            df = pd.read_csv(file_path, sep=inferred_sep, index_col=0)

        df.fillna(0, inplace=True)

        return df

    def _cluster_data(self, df, dist_metric, linkage_method):

        logging.info('Start clustering data with distance metric {} and linkage method {}'.format(
                                                                    dist_metric, linkage_method))

        col_ordered_label = self._compute_cluster_label_order(df.T.values.tolist(),
                                                              df.T.index.tolist(),
                                                              dist_metric=dist_metric,
                                                              linkage_method=linkage_method)

        idx_ordered_label = self._compute_cluster_label_order(df.values.tolist(),
                                                              df.index.tolist(),
                                                              dist_metric=dist_metric,
                                                              linkage_method=linkage_method
                                                              )

        df = df.reindex(index=idx_ordered_label, columns=col_ordered_label)

        return df

    def _build_heatmap_data(self, data_df):

        logging.info('Start building heatmap data')

        heatmap_data = dict()

        heatmap_data['values'] = data_df.values.tolist()
        heatmap_data['x_labels'] = data_df.columns.tolist()
        heatmap_data['y_labels'] = data_df.index.tolist()

        return heatmap_data

    def _generate_heatmap_report(self, heatmap_data):
        logging.info('Start generating heatmap report')

        output_directory = os.path.join(self.scratch, str(uuid.uuid4()))
        logging.info('Start building report files in dir: {}'.format(output_directory))
        self._mkdir_p(output_directory)

        heatmap_data_json = os.path.join(output_directory, 'heatmap_data_{}.json'.format(
                                                                                str(uuid.uuid4())))
        with open(heatmap_data_json, 'w') as outfile:
            json.dump(heatmap_data, outfile)

        heatmap_html = os.path.join(output_directory, 'heatmap_report_{}.html'.format(
                                                                                str(uuid.uuid4())))
        with open(heatmap_html, 'w') as heatmap_html:
            with open(os.path.join(os.path.dirname(__file__),
                                   'templates', 'heatmap_template.html'),
                      'r') as heatmap_template_file:
                heatmap_template = heatmap_template_file.read()
                heatmap_template = heatmap_template.replace('heatmap_data_json_file_name',
                                                            os.path.basename(heatmap_data_json))
                heatmap_html.write(heatmap_template)

        return output_directory

    def __init__(self, config):
        self.callback_url = config['SDK_CALLBACK_URL']
        self.endpoint = config['kbase-endpoint']
        self.scratch = config['scratch']
        self.token = config['KB_AUTH_TOKEN']

        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        self.obj_cache = dict()

        plt.switch_backend('agg')
        sys.setrecursionlimit(150000)

    def build_heatmap_html(self, params):

        tsv_file_path = params.get('tsv_file_path')

        data_df = self._read_csv_file(tsv_file_path)
        if params.get('cluster_data', True):
            dist_metric = params.get('dist_metric', 'euclidean')
            linkage_method = params.get('linkage_method', 'ward')
            data_df = self._cluster_data(data_df, dist_metric, linkage_method)
        heatmap_data = self._build_heatmap_data(data_df)
        heatmap_html_dir = self._generate_heatmap_report(heatmap_data)

        return {'html_dir': heatmap_html_dir}
