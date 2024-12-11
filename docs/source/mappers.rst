==============================
Mappings for Non-CEDA Catalogs
==============================

DataPoint was developed primarily to support data users for accessing the CEDA archive of data via CEDA STAC Catalogs. 
These catalogs have a specific arrangement of properties and attributes within each record that DataPoint uses for configuration i.e to open a dataset.
We recognise that other organisations will have their own layout for STAC catalogs and their own specific property names. To that end, the ``DataPointMapper`` was created
which allows a simple mapping to be applied to inform DataPoint of how to reach specific properties (if they are present) in any arrangement of STAC records.

1. Item Mappings
----------------

There are a number of item-level attributes DataPoint expects to find; those being ``id``, ``properties`` and ``assets``. Additionally, DataPoint uses the ``cloud_format`` property of each asset to
determine suitability for opening as a ``Cloud Product``, i.e for Kerchunk/Zarr data. This is not applicable for NetCDF/HDF or other archival formats directly. The cloud format mapping should
be treated as applying to all assets under whatever asset mapping is used.

.. code::

    item_mappings = {
        "id":"properties.id",
        "properties":"properties",
        "assets":"properties.model.assets",
        "cloud_format":"cloud_format"
    }

    search = client.search(..., mappings=item_mappings)

In this example, most of the expected attributes are found under ``properties`` for each item in this example, with the ``assets`` nested under a few layers of labels. The ``cloud_format`` in this case
will be applied to all objects under ``properties.model.assets``. Note the syntax for nested layers here is to use a ``.`` between sections, so this attribute would expand to ``{"properties":{"models":{"assets":[]}}}``
in the STAC record.

2. Asset Mappings
-----------------

Assets may have the same or different mappings to the items, so at the point of retrieving the desired cloud assets it is necessary to supply asset mappings in the same way as before.

.. code::

    asset_mappings = {
        "href":"properties.href",
        "mapper_kwargs":"kerchunk_kwargs",
        "open_zarr_kwargs":"zarr_kwargs",
        "open_xarray_kwargs":"xarray_kwargs",
        "open_cog_kwargs":"cog_kwargs"
    }

    cluster = search.collect_cloud_assets(..., asset_mappings=asset_mappings)

    # Any attempt to access cloud assets can be used to inject the asset mappings, e.g.

    ds = search.open_dataset(id, asset_mappings=asset_mappings)

In this case the attribute ``href``, which is required for all cloud assets by DataPoint, is under the ``properties`` attribute of each asset itself - very unusual!
Other attributes are found at the top-level of the asset, but under a different name. Importantly, the asset mappings can be provided at any point where assets are accessed. 
For example in the last line, a dataset is opened directly from the search object, but the mappings are still required to allow the configurations needed to open the dataset.
