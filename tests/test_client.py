from ceda_datapoint import DataPointClient

def test_main():
    dpc = DataPointClient(hash_token='lonestar')

    assert hasattr(dpc, 'meta')
    assert str(dpc) == '<DataPointClient: CEDA-333146>'

if __name__ == '__main__':
    test_main()