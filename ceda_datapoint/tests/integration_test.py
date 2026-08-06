"""Integration test for opening datasets using CEDA Datapoint."""

import unittest
import ceda_datapoint
from ceda_datapoint import DataPointClient



def setup_cluster(collection, search_query, verbose=False, use_client=False):
    """Set up and return a Datapoint client, search and cluster."""
    if use_client:
        client = use_client  # use an existing client, not a new one
    else:
        client = DataPointClient(org="CEDA")

    if verbose:
        print(
            client,
            client.info(),
            client.help(),
            client.list_collections(),
            client.list_query_terms(collection=collection),
        )

    search = client.search(
        collections=[collection],
        **search_query,
    )
    if verbose:
        print(
            search,
            search.info(),
            search.help(),
            search.display_assets(),
            search.display_cloud_assets(),
            search.items,
        )

    cluster = search.collect_cloud_assets()
    if verbose:
        print(
            cluster,
            cluster.info(),
            cluster.help(),
            cluster.products,
        )

    return client, search, cluster


class TestDataPointIntegration(unittest.TestCase):
    """Integration test for opening STAC datasets."""

    @classmethod
    def setUpClass(cls):
        """Set up the test class."""
        # Set True for more info / debugging
        cls.verbose = False

        collection = "cmip6"
        basic_search_inputs = {
            "query": [
                "cmip6:experiment_id=ssp585",
                "cmip6:activity_id=ScenarioMIP",
                "cmip6:institution_id=KIOST"
            ],
            "max_items": 10,
        }
        cls.client, cls.search_basic, cls.cluster = setup_cluster(
            collection, basic_search_inputs, verbose=cls.verbose
        )


        # A search requiring 'preparation' of the dataset
        # Using example from docs at: https://cedadev.github.io/datapoint/index.html
        compound_search_inputs = {
            "query": [
                'cmip6:experiment_id=001',
                'variables=clt',
            ],
            "intersects": {
                "type": "Polygon",
                "coordinates": [[[6, 53], [7, 53], [7, 54], [6, 54], [6, 53]]],
            },
            "datetime": '2025-01-01/2025-12-31',
            "data_selection": {
                'variables': ['clt'],
                'sel':{
                    'nv': slice(0,5)
                }
            },
            "max_items": 10,
        }
        _, cls.search_compound, cls.cluster_compound = setup_cluster(
            collection, compound_search_inputs, verbose=cls.verbose,
            use_client=cls.client,
        )

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

        txt = str(refs)

        # Prevent whole kerchunk ref text spamming terminal for failure cases
        self.longMessage = False

        self.assertNotIn(
            "file://",
            txt,
            msg="Kerchunk reference contains 'file://' but should not",
        )
        self.assertNotIn(
            "https://",
            txt,
            msg="Kerchunk reference contains 'https://' but should not",
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

    def test_product_simple_open_with_xarray_local_only(self):
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

    def test_cluster_simple_open_with_xarray(self):
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

    def test_cluster_simple_open_with_xarray_local_only(self):
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

    def test_product_simple_open_with_cf(self):
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

    def test_product_simple_open_with_cf_local_only(self):
        """Test opening local-only datasets from a product in 'cf' mode."""
        prod = self.cluster[0]
        if self.verbose:
            print(
                prod,
                prod.info(),
                prod.help(),
                prod.attributes,
            )

        # 'local_only' not supported for cf-python mode
        with self.assertRaises(ValueError):
            fl = prod.open_dataset(mode="cf", local_only=True)

    def test_cluster_simple_open_with_cf(self):
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

    def test_cluster_simple_open_with_cf_local_only(self):
        """Test opening local-only datasets from a cluster in 'cf' mode."""
        cluster = self.cluster
        if self.verbose:
            print(
                cluster,
                cluster.info(),
                cluster.help(),
            )

        # 'local_only' not supported for cf-python mode
        with self.assertRaises(ValueError):
            fl = cluster.open_dataset(id=0, mode="cf", local_only=True)


if __name__ == "__main__":
    unittest.main()
