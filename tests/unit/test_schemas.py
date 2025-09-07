from src.models.schemas import ItemBase, ItemCreate, Item

def test_item_base_schema():
    item_data = {"name": "Test Item", "description": "A test description"}
    item = ItemBase(**item_data)
    assert item.name == "Test Item"
    assert item.description == "A test description"

def test_item_base_schema_no_description():
    item_data = {"name": "Another Item"}
    item = ItemBase(**item_data)
    assert item.name == "Another Item"
    assert item.description is None

def test_item_create_schema():
    item_data = {"name": "New Item", "description": "Description for new item"}
    item = ItemCreate(**item_data)
    assert item.name == "New Item"
    assert item.description == "Description for new item"

def test_item_schema():
    item_data = {"id": 1, "name": "Existing Item", "description": "Description for existing item"}
    item = Item(**item_data)
    assert item.id == 1
    assert item.name == "Existing Item"
    assert item.description == "Description for existing item"

def test_item_schema_from_attributes():
    class MockDBItem:
        id = 2
        name = "Mock Item"
        description = "From DB"

    mock_item = MockDBItem()
    item = Item.model_validate(mock_item)
    assert item.id == 2
    assert item.name == "Mock Item"
    assert item.description == "From DB"
