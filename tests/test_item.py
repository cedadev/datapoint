from ceda_datapoint.core.item import DataPointItem

class TestItem:
    def __init__(self, id='test_item1'):

        self.id = id

    def to_dict(self):
        return {
        }
    
    def get_collection(self):
        return TestItem(id='test_collection')


def test_main():

    test_item = TestItem()
    test_meta = {
        
    }

    item = DataPointItem(test_item, meta=test_meta)