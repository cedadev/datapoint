"""Intergration test for opening datasets using CEDA Datapoint."""

import unittest
from ceda_datapoint import DataPointClient


def setup_cluster(query, collection, verbose=False):
    """Set up and return a Datapoint client, search and cluster."""
    client = DataPointClient(org="CEDA")
    if verbose:
        print(
            client,
            client.info(),
            client.help(),
            client.list_collections(),
            client.list_query_terms(collection=collection),
        )

    search_basic = client.search(collections=[collection], query=query, max_items=10)
    if verbose:
        print(
            search_basic,
            search_basic.info(),
            search_basic.help(),
            search_basic.display_assets(),
            search_basic.display_cloud_assets(),
            search_basic.items,
        )

    search_basic._load_asset_set()

    cluster = search_basic.collect_cloud_assets()
    if verbose:
        print(
            cluster,
            cluster.info(),
            cluster.help(),
            cluster.products,
        )

    return client, search_basic, cluster


class TestDataPointIntegration(unittest.TestCase):
    """Integration test for opening STAC datasets."""

    @classmethod
    def setUpClass(cls):
        """Set up the test class."""
        # Set True for more info / debugging
        cls.verbose = False

        collection = "cmip6"
        query = [
            "cmip6:experiment_id=ssp585",
            "cmip6:activity_id=ScenarioMIP",
            "cmip6:institution_id=KIOST",
        ]
        cls.client, cls.search_basic, cls.cluster = setup_cluster(
            query, collection, verbose=cls.verbose
        )

    def test_cluster_setup(self):
        """Test the setting up of a cluster."""
        self.assertIsNotNone(self.cluster)
        # TODO further assertions

    def test_open_with_xarray(self):
        """Test opening datasets in 'xarray' mode."""
        prod = self.cluster[0]
        if self.verbose:
            print(
                prod,
                prod.info(),
                prod.help(),
                prod.attributes,
            )

        ds = prod.open_dataset(mode="xarray")
        self.assertIsNotNone(ds)
        # TODO further assertions

    def test_open_with_cf(self):
        """Test opening datasets in 'cf' mode."""
        prod = self.cluster[0]
        if self.verbose:
            print(
                prod,
                prod.info(),
                prod.help(),
                prod.attributes,
            )

        fl = prod.open_dataset(mode="cf")
        self.assertIsNotNone(fl)
        # TODO further assertions


if __name__ == "__main__":
    unittest.main()
