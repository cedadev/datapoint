from datapoint import DataPointClient

client = DataPointClient()

item_cfa = client.search(
    collections=['cmip6'],
    query=[
        'experiment_id=ssp119',
        'table_id=3hr',
        'institution_id=CNRM-CERFACS',
        'variant_label=r1i1p1f2',
        'activity_id=ScenarioMIP',
        'mip_era=CMIP6',
        'cf_standard_name=specific_humidity'
    ]
)[0]

print(item_cfa.open_dataset(priority=['reference_file_2']))