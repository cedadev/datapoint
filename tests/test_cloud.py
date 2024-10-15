from ceda_datapoint.core.cloud import DataPointCluster

def test_cluster():
    dpc = DataPointCluster([], 'test_search',meta={})
    assert hasattr(dpc, 'meta')

if __name__ == '__main__':
    test_cluster()