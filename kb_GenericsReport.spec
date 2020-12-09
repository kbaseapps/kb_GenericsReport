/*
A KBase module: kb_GenericsReport
*/

module kb_GenericsReport {

    /* A boolean - 0 for false, 1 for true.
    */
    typedef int boolean;

    typedef structure {
        string html_dir;
    } build_heatmap_html_result;

    /*
      required params:
      tsv_file_path: matrix data in tsv format

      optional params:
      cluster_data: True if data should be clustered. Default: True
      sort_by_sum: True if data should be sorted by sum of values. Default: False
      top_percent: Only display top x percent of data. Default: 100
      centered_by: set midpoint of color range. Default: None
      dist_metric: distance metric used for clustering. Default: euclidean (https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.pdist.html)
      linkage_method: linkage method used for clustering. Default: ward (https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html)

    */
    typedef structure {
        string tsv_file_path;

        boolean cluster_data;
        boolean sort_by_sum;
        int top_percent;
        float centered_by;
        string dist_metric;
        string linkage_method;
    } build_heatmap_html_params;

    funcdef build_heatmap_html(build_heatmap_html_params params) returns (build_heatmap_html_result output) authentication required;

};
