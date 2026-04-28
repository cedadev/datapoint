from ceda_datapoint import DataPointClient


def setup_cluster(verbose=False):
    """Set up the cluster ready to test opening of dataset products.

    This is based on the set up from the Notebook demo/basic_usage.ipynb.
    """

    # 1. Set up client
    client = DataPointClient(org='CEDA')
    if verbose:
        # Print info about client
        print(
            client,
            client.info(),
            client.help(),
            client.list_collections(),
            client.list_query_terms(collection='cmip6')
        )

    # 2. Set up a (basic) search
    search_basic = client.search(
        collections=['cmip6'],
        query=[
            'cmip6:experiment_id=ssp585',
            'cmip6:activity_id=ScenarioMIP',
            'cmip6:institution_id=KIOST',
        ],
        max_items = 10
    )
    if verbose:
        # Print info about search
        print(
            search_basic,
            search_basic.info(),
            search_basic.help(),
            search_basic.display_assets(),
            search_basic.display_cloud_assets(),
            search_basic.items
        )

    search_basic._load_asset_set()

    # 3. Set up a cluster
    cluster = search_basic.collect_cloud_assets()
    if verbose:
        # Print info about cluster
        print(
            cluster,
            cluster.info(),
            cluster.help(),
            cluster.products,
        )

    return client, search_basic, cluster


def test_xarray_open(cluster, product_id_or_index, verbose=False):
    """Test the opening of cloud products using xarray."""
    prod = cluster[product_id_or_index]
    if verbose:
        print(
            prod,
            prod.info(),
            prod.help(),
            prod.attributes,
        )

    ds = prod.open_dataset(mode="xarray")
    print(ds)


def test_cf_open(cluster, product_id_or_index, verbose=False):
    """Test the opening of cloud products using cf-python."""
    prod = cluster[product_id_or_index]
    if verbose:
        print(
            prod,
            prod.info(),
            prod.help(),
            prod.attributes,
        )

    fl = prod.open_dataset(mode="cf")
    print(fl)


def run_tests():
    """Test the opening of cloud products under any mode of open."""
    cluster = setup_cluster()[2]

    test_product_ids = [
        0,
        #2,
        #'CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.vas.gr1.v20191106-reference_file',
    ]
    for product in test_product_ids:
        test_xarray_open(cluster, product)
        test_cf_open(cluster, product, verbose=True)
        print(f">>>>>>>>>>>>>>>>>>>>>> Pass for {product}")


if __name__ == "__main__":
    run_tests()
