from ceda_datapoint.core.cloud import DataPointCluster


class TestCluster:
    def test_main(self):
        dpc = DataPointCluster([], 'test_search',meta={})
        assert hasattr(dpc, 'meta')

if __name__ == '__main__':
    TestCluster().test_main()