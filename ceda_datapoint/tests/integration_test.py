"""Intergration test for opening datasets using CEDA Datapoint."""

import unittest
import ceda_datapoint
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

    search_basic = client.search(
        collections=[collection],
        query=query,
        max_items=10
    )
    if verbose:
        print(
            search_basic,
            search_basic.info(),
            search_basic.help(),
            search_basic.display_assets(),
            search_basic.display_cloud_assets(),
            search_basic.items,
        )

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

    def check_local_only(self, product):
        """Check HREF is a local case."""
        # Only kerchunk is valid for local_only case
        self.assertEqual(
            product._cloud_format,
            "kerchunk",
            "local_only behaviour is only valid for kerchunk datasets"
        )

        refs = ceda_datapoint.core.cloud._fetch_kerchunk_make_local(
            product.href)
        self.assertIn("file://", str(refs))

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

    def test_product_open_with_xarray(self):
        """Test opening datasets from a product in 'xarray' mode."""
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

    def test_product_open_with_xarray_local_only(self):
        """Test opening local-only datasets from a product in 'xarray' mode."""
        prod = self.cluster[0]
        if self.verbose:
            print(
                prod,
                prod.info(),
                prod.help(),
                prod.attributes,
            )

        self.check_local_only(prod)

        ds = prod.open_dataset(mode="xarray", local_only=True)

        self.assertIsNotNone(ds)

        print("\nXR LOCAL ONLY DATASET IS:\n", ds)
        # TODO further assertions

    def test_cluster_open_with_xarray(self):
        """Test opening datasets from a cluster in 'xarray' mode."""
        cluster = self.cluster
        if self.verbose:
            print(
                cluster,
                cluster.info(),
                cluster.help(),
                cluster.attributes,
            )

        # TODO test with loop over various products (not just id=0 case)
        ds = cluster.open_dataset(id=0, mode="xarray")
        self.assertIsNotNone(ds)
        # TODO further assertions

    def test_cluster_open_with_xarray_local_only(self):
        """Test opening local-only datasets from a cluster in 'xarray' mode."""
        cluster = self.cluster
        if self.verbose:
            print(
                cluster,
                cluster.info(),
                cluster.help(),
            )

        product_id = 0
        self.check_local_only(cluster[product_id])

        # TODO test with loop over various products (not just id=0 case)
        ds = cluster.open_dataset(id=product_id, mode="xarray", local_only=True)

        self.assertIsNotNone(ds)
        # TODO further assertions

    def test_product_open_with_cf(self):
        """Test opening datasets from a product in 'cf' mode."""
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

        #print("\nCF FIELDLIST IS:\n", fl)
        #print("\nFIRST FIELD IS:\n", fl[0])
        # TODO further assertions

    def test_product_open_with_cf_local_only(self):
        """Test opening local-only datasets from a product in 'cf' mode."""
        prod = self.cluster[0]
        if self.verbose:
            print(
                prod,
                prod.info(),
                prod.help(),
                prod.attributes,
            )

        self.check_local_only(prod)

        fl = prod.open_dataset(mode="cf", local_only=True)

        self.assertIsNotNone(fl)

        print("\nCF LOCAL ONLY FIELDLIST IS:\n", fl)
        print("\nFIRST LOCAL ONLY FIELD IS:\n", fl[0])
        # TODO further assertions

    def test_cluster_open_with_cf(self):
        """Test opening datasets from a cluster in 'cf' mode."""
        cluster = self.cluster
        if self.verbose:
            print(
                cluster,
                cluster.info(),
                cluster.help(),
            )

        # TODO test with loop over various products (not just id=0 case)
        fl = cluster.open_dataset(id=0, mode="cf")
        self.assertIsNotNone(fl)
        # TODO further assertions

    def test_cluster_open_with_cf_local_only(self):
        """Test opening local-only datasets from a cluster in 'cf' mode."""
        cluster = self.cluster
        if self.verbose:
            print(
                cluster,
                cluster.info(),
                cluster.help(),
            )

        product_id = 0
        self.check_local_only(cluster[product_id])

        # TODO test with loop over various products (not just id=0 case)
        fl = cluster.open_dataset(id=product_id, mode="cf", local_only=True)

        self.assertIsNotNone(fl)
        # TODO further assertions


if __name__ == "__main__":
    unittest.main()
