from ceda_datapoint import DataPointClient

def test_main():
    dpc = DataPointClient()

    assert hasattr(dpc, 'meta')