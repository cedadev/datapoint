from ceda_datapoint.core.item import DataPointItem


class ExampleItem:
    def __init__(self, id='test_item1'):

        self.id = id

    def __contains__(self, item):
        if item in ['id']:
            return True
        
    def __getitem__(self, item):
        if item == 'id':
            return self.id
        if item == 'assets':
            return []

    def to_dict(self):
        return {
            'test':'test_value',
            'assets':[]
        }
    
    def get_collection(self):
        return ExampleItem(id='test_collection')

class TestItem:
    def test_main(self):

        test_item = ExampleItem()
        test_meta = {}

        item = DataPointItem(test_item, meta=test_meta)
        assert hasattr(item, '_meta')

if __name__ == '__main__':
    TestItem().test_main()