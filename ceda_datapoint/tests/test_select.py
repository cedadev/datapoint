from ceda_datapoint import DataPointClient

client = DataPointClient()

search = client.search(
    collections=['cmip6'],
    intersects={
        "type": "Polygon",
        "coordinates": [[[6, 53], [15, 53], [15, 60], [6, 60], [6, 53]]],
    }, 
    #datetime='2500-01-01/4094-01-01',
    data_selection={
        'sel':{'lat':slice(8,10)}
    },
    max_items = 10)

cluster = search.collect_cloud_assets()
print(cluster[0].open_dataset())