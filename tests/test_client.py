from ceda_datapoint import DataPointClient

def test_main():
    dpc = DataPointClient()

    assert hasattr(dpc, 'meta')

if __name__ == '__main__':
    test_main()