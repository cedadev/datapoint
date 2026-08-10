"""Integration test for opening datasets using CEDA Datapoint."""

from contextlib import contextmanager
import os
import unittest
import unittest.mock  # not provided in above general import by default

import ceda_datapoint
from ceda_datapoint import DataPointClient
import cf
import numpy as np


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


def requires_ceda_filesystem(test):
    """Test to enable skipping tests requiring the CEDA filesystem."""
    return unittest.skipUnless(
        os.path.isdir("/badc"),
        "Requires CEDA filesystem mounted at /badc",
    )(test)


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
        # Search inputs based on example from docs at:
        #     https://cedadev.github.io/datapoint/index.html
        compound_search_inputs = {
            "query": [
                'cmip6:activity_id=ScenarioMIP',
            ],
            "intersects": {
                "type": "Polygon",
                "coordinates": [[
                    [100, -45], [300, 45], [350, 45], [300, 90], [100, -45]
                ]],
            },
            "datetime": '2201-01-01/2210-01-01',
            "data_selection": {
                'variables': ['tasmin',],
                 'sel':{
                     'lon': slice(100, 150),
                     'lat': slice(0, 30)
                 }
            },
            "max_items": 10,
        }
        _, cls.search_compound, cls.cluster_compound = setup_cluster(
            collection, compound_search_inputs, verbose=cls.verbose,
            use_client=cls.client,
        )

    @contextmanager
    def check_local_only(self):
        """Check that `local_only` uses local kerchunk references."""

        original_fetch = ceda_datapoint.core.cloud._fetch_kerchunk_make_local
        captured_refs = []

        def fetch_and_capture(href):
            refs = original_fetch(href)
            captured_refs.append(refs)
            return refs

        # Prevent whole kerchunk ref text spamming terminal for failure cases
        self.longMessage = False

        with unittest.mock.patch(
            "ceda_datapoint.core.cloud._fetch_kerchunk_make_local",
            side_effect=fetch_and_capture,
        ) as fetch_mock:
            yield

        self.assertTrue(
            fetch_mock.called,
            "_fetch_kerchunk_make_local was not called",
        )

        for refs in captured_refs:
            txt = str(refs)

            self.assertNotIn(
                "https://dap.ceda.ac.uk",
                txt,
                msg="Kerchunk reference still contains a CEDA URL",
            )

    def check_prsn_dataset_xr(self, ds):
        """Check data matches expected CMIP6 'prsn' field with xarray."""
        # Dataset dimensions
        self.assertEqual(
            dict(ds.sizes),
            {
                "lat": 96,
                "bnds": 2,
                "lon": 192,
                "time": 1032,
            },
        )

        # Coordinates
        self.assertEqual(
            set(ds.coords),
            {"lat", "lon", "time"},
        )

        self.assertEqual(ds["lat"].dims, ("lat",))
        self.assertEqual(ds["lon"].dims, ("lon",))
        self.assertEqual(ds["time"].dims, ("time",))

        self.assertEqual(ds["lat"].dtype, np.dtype("float64"))
        self.assertEqual(ds["lon"].dtype, np.dtype("float64"))

        # Coordinate values
        self.assertAlmostEqual(float(ds["lat"].values[0]), -89.0625)
        self.assertAlmostEqual(float(ds["lat"].values[-1]), 89.0625)

        self.assertAlmostEqual(float(ds["lon"].values[0]), 0.9375)
        self.assertAlmostEqual(float(ds["lon"].values[-1]), 359.0625)

        # Data variables
        self.assertEqual(
            set(ds.data_vars),
            {
                "lat_bnds",
                "lon_bnds",
                "prsn",
                "time_bnds",
            },
        )

        self.assertEqual(ds["lat_bnds"].dims, ("lat", "bnds"))
        self.assertEqual(ds["lon_bnds"].dims, ("lon", "bnds"))
        self.assertEqual(ds["prsn"].dims, ("time", "lat", "lon"))
        self.assertEqual(ds["time_bnds"].dims, ("time", "bnds"))

        # Variable dtypes
        self.assertEqual(ds["lat_bnds"].dtype, np.dtype("float64"))
        self.assertEqual(ds["lon_bnds"].dtype, np.dtype("float64"))
        self.assertEqual(ds["prsn"].dtype, np.dtype("float32"))

        # Time coverage
        self.assertEqual(ds["time"].values[0].year, 2015)
        self.assertEqual(ds["time"].values[0].month, 1)
        self.assertEqual(ds["time"].values[0].day, 17)

        self.assertEqual(ds["time"].values[-1].year, 2100)
        self.assertEqual(ds["time"].values[-1].month, 12)
        self.assertEqual(ds["time"].values[-1].day, 17)

        # Dataset metadata
        self.assertEqual(ds.attrs["activity_id"], "ScenarioMIP")
        self.assertEqual(ds.attrs["table_id"], "Amon")
        self.assertEqual(ds.attrs["variable_id"], "prsn")
        self.assertEqual(ds.attrs["variant_label"], "r1i1p1f1")
        self.assertEqual(
            ds.attrs["title"],
            "KIOST-ESM output prepared for CMIP6",
        )
        self.assertEqual(
            ds.attrs["Conventions"],
            "CF-1.7 CMIP-6.2",
        )

    def check_prsn_dataset_cf(self, field):
        """Check data matches expected CMIP6 'prsn' field with cf-python."""
        # Field identity and data
        self.assertEqual(
            field.nc_get_variable(),
            "prsn",
        )
        self.assertEqual(
            field.get_property("standard_name"),
            "snowfall_flux",
        )
        self.assertEqual(
            field.get_property("long_name"),
            "Snowfall Flux",
        )
        self.assertEqual(
            field.get_property("units"),
            "kg m-2 s-1",
        )
        self.assertEqual(
            field.shape,
            (1032, 96, 192),
        )
        self.assertEqual(
            field.ndim,
            3,
        )

        # Field properties
        expected_properties = {
            "activity_id": "ScenarioMIP",
            "experiment_id": "ssp585",
            "frequency": "mon",
            "grid_label": "gr1",
            "institution_id": "KIOST",
            "mip_era": "CMIP6",
            "source_id": "KIOST-ESM",
            "table_id": "Amon",
            "variable_id": "prsn",
            "variant_label": "r1i1p1f1",
        }
        for name, expected in expected_properties.items():
            self.assertEqual(
                field.get_property(name),
                expected,
                msg=f"Unexpected value for field property {name!r}",
            )

        # Cell methods
        cell_methods = field.cell_methods()

        self.assertEqual(
            len(cell_methods),
            1,
        )

        cell_method = cell_methods["cellmethod0"]
        self.assertEqual(
            cell_method.get_method(),
            "mean",
        )
        self.assertEqual(
            cell_method.get_axes(),
            ("area", "domainaxis0"),
        )
        print(field.constructs(), field.construct("time", key=True))

        # Dimension coordinates
        time = field.coordinate("T")
        latitude = field.coordinate("Y")
        longitude = field.coordinate("X")

        self.assertEqual(
            time.identity(),
            "time",
        )
        self.assertEqual(
            latitude.identity(),
            "latitude",
        )
        self.assertEqual(
            longitude.identity(),
            "longitude",
        )
        self.assertEqual(
            time.shape,
            (1032,),
        )
        self.assertEqual(
            latitude.shape,
            (96,),
        )
        self.assertEqual(
            longitude.shape,
            (192,),
        )

        # Time coordinate
        self.assertEqual(
            time.get_property("standard_name"),
            "time",
        )
        self.assertEqual(
            time.get_property("long_name"),
            "time",
        )
        self.assertEqual(
            time.get_property("units"),
            "days since 1850-01-01",
        )
        self.assertEqual(
            time.get_property("calendar"),
            "365_day",
        )
        self.assertEqual(
            time.get_property("axis"),
            "T",
        )

        # Time bounds
        time_bounds = time.get_bounds()

        self.assertIsNotNone(time_bounds)
        self.assertEqual(
            time_bounds.shape,
            (1032, 2),
        )
        self.assertEqual(
            time_bounds.get_property("calendar"),
            "365_day",
        )
        self.assertEqual(
            time_bounds.get_property("units"),
            "days since 1850-01-01",
        )

        # Latitude coordinate
        self.assertEqual(
            latitude.get_property("standard_name"),
            "latitude",
        )
        self.assertEqual(
            latitude.get_property("long_name"),
            "Latitude",
        )
        self.assertEqual(
            latitude.get_property("units"),
            "degrees_north",
        )
        self.assertEqual(
            latitude.get_property("axis"),
            "Y",
        )
        self.assertEqual(
            latitude.get_bounds().shape,
            (96, 2),
        )
        self.assertEqual(
            latitude.get_bounds().get_property("units"),
            "degrees_north",
        )

        # Longitude coordinate
        self.assertEqual(
            longitude.get_property("standard_name"),
            "longitude",
        )
        self.assertEqual(
            longitude.get_property("long_name"),
            "Longitude",
        )
        self.assertEqual(
            longitude.get_property("units"),
            "degrees_east",
        )
        self.assertEqual(
            longitude.get_property("axis"),
            "X",
        )
        self.assertEqual(
            longitude.get_bounds().shape,
            (192, 2),
        )
        self.assertEqual(
            longitude.get_bounds().get_property("units"),
            "degrees_east",
        )

    def test_cluster_setup(self):
        """Test the setting up of a cluster."""
        self.assertIsNotNone(self.cluster)
        # TODO further assertions

    # Simple search tests below

    def test_product_simple_open_with_xarray(self):
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

        # Dataset was successfully opened
        self.assertIsNotNone(ds)

        # Then check the Dataset is as expected
        self.check_prsn_dataset_xr(ds)

    @requires_ceda_filesystem
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

        with self.check_local_only():
            ds = prod.open_dataset(mode="xarray", local_only=True)

        # Dataset was successfully opened
        self.assertIsNotNone(ds)

        # Then check the Dataset is as expected
        self.check_prsn_dataset_xr(ds)

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

        # Dataset was successfully opened
        self.assertIsNotNone(ds)

        # Then check the Dataset is as expected
        self.check_prsn_dataset_xr(ds)

    @requires_ceda_filesystem
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
        with self.check_local_only():
            # TODO test with loop over various products (not just id=0 case)
            ds = cluster.open_dataset(id=product_id, mode="xarray", local_only=True)

        # Dataset was successfully opened
        self.assertIsNotNone(ds)

        # Then check the Dataset is as expected
        self.check_prsn_dataset_xr(ds)

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

        # Data was successfully opened and converted to a CF FieldList
        self.assertIsNotNone(fl)
        self.assertIsInstance(fl, cf.FieldList)
        self.assertEqual(len(fl), 1)
        f = fl[0]  # only one Field in FieldList, unpack it
        self.assertIsInstance(f, cf.Field)

        # Then check the one Field is as expected
        self.check_prsn_dataset_cf(f)

    @requires_ceda_filesystem
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

        # Data was successfully opened and converted to a CF FieldList
        self.assertIsNotNone(fl)
        self.assertIsInstance(fl, cf.FieldList)
        self.assertEqual(len(fl), 1)
        f = fl[0]  # only one Field in FieldList, unpack it
        self.assertIsInstance(f, cf.Field)

        # Then check the one Field is as expected
        self.check_prsn_dataset_cf(f)

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

        # Data was successfully opened and converted to a CF FieldList
        self.assertIsNotNone(fl)
        self.assertIsInstance(fl, cf.FieldList)
        self.assertEqual(len(fl), 1)
        f = fl[0]  # only one Field in FieldList, unpack it
        self.assertIsInstance(f, cf.Field)

        # Then check the one Field is as expected
        self.check_prsn_dataset_cf(f)

    @requires_ceda_filesystem
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

        # Data was successfully opened and converted to a CF FieldList
        self.assertIsNotNone(fl)
        self.assertIsInstance(fl, cf.FieldList)
        self.assertEqual(len(fl), 1)
        f = fl[0]  # only one Field in FieldList, unpack it
        self.assertIsInstance(f, cf.Field)

        # Then check the one Field is as expected
        self.check_prsn_dataset_cf(f)

    # Compound search tests below

    def test_product_compound_open_with_xarray(self):
        """Test opening datasets from a product in 'xarray' mode."""
        prod = self.cluster_compound[0]
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

    @requires_ceda_filesystem
    def test_product_compound_open_with_xarray_local_only(self):
        """Test opening local-only datasets from a product in 'xarray' mode."""
        prod = self.cluster_compound[0]
        if self.verbose:
            print(
                prod,
                prod.info(),
                prod.help(),
                prod.attributes,
            )

        with self.check_local_only():
            ds = prod.open_dataset(mode="xarray", local_only=True)

        self.assertIsNotNone(ds)
        # TODO further assertions

    def test_cluster_compound_open_with_xarray(self):
        """Test opening datasets from a cluster in 'xarray' mode."""
        cluster = self.cluster_compound
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

    @requires_ceda_filesystem
    def test_cluster_compound_open_with_xarray_local_only(self):
        """Test opening local-only datasets from a cluster in 'xarray' mode."""
        cluster = self.cluster_compound
        if self.verbose:
            print(
                cluster,
                cluster.info(),
                cluster.help(),
            )

        product_id = 0
        with self.check_local_only():
            # TODO test with loop over various products (not just id=0 case)
            ds = cluster.open_dataset(id=product_id, mode="xarray", local_only=True)

        self.assertIsNotNone(ds)
        # TODO further assertions

    def test_product_compound_open_with_cf(self):
        """Test opening datasets from a product in 'cf' mode."""
        prod = self.cluster_compound[0]
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

    @requires_ceda_filesystem
    def test_product_compound_open_with_cf_local_only(self):
        """Test opening local-only datasets from a product in 'cf' mode."""
        prod = self.cluster_compound[0]
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

    def test_cluster_compound_open_with_cf(self):
        """Test opening datasets from a cluster in 'cf' mode."""
        cluster = self.cluster_compound
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

    @requires_ceda_filesystem
    def test_cluster_compound_open_with_cf_local_only(self):
        """Test opening local-only datasets from a cluster in 'cf' mode."""
        cluster = self.cluster_compound
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
