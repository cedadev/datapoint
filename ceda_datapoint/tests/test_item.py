from ceda_datapoint.core.item import DataPointItem

class ExampleItem:
    def __init__(self, id='test_item1'):

        self.id = id

    def to_dict(self):
        return {
            'test':'test_value',
            'assets':[]
        }
    
    def get_collection(self):
        return ExampleItem(id='test_collection')

def test_main():

    test_item = ExampleItem()
    test_meta = {}

    item = DataPointItem(test_item, meta=test_meta)
    assert hasattr(item, '_meta')

if __name__ == '__main__':
    test_main()