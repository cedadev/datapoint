from ceda_datapoint import DataPointClient


class TestClient:
    def test_main(self):
        dpc = DataPointClient(hash_token='lonestar')

        assert hasattr(dpc, 'meta')
        assert str(dpc) == '<DataPointClient: CEDA-333146>'

if __name__ == '__main__':
    TestClient().test_main()