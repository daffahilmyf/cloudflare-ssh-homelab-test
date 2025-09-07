import pytest
from src.services.item_service import ItemService
from src.models.schemas import ItemCreate, Item, ItemUpdate

@pytest.fixture
def mock_db():
    return {
        1: {"id": 1, "name": "Test Item 1", "description": "Description 1"},
        2: {"id": 2, "name": "Test Item 2", "description": "Description 2"},
    }

@pytest.fixture
def item_service(mock_db):
    return ItemService(mock_db)

@pytest.mark.asyncio
async def test_get_items(item_service):
    items = await item_service.get_items()
    assert len(items) == 2
    assert all(isinstance(item, Item) for item in items)
    assert items[0].name == "Test Item 1"

@pytest.mark.asyncio
async def test_get_item_existing(item_service):
    item = await item_service.get_item(1)
    assert item is not None
    assert item.id == 1
    assert item.name == "Test Item 1"

@pytest.mark.asyncio
async def test_get_item_non_existing(item_service):
    item = await item_service.get_item(999)
    assert item is None

@pytest.mark.asyncio
async def test_create_item(item_service, mock_db):
    new_item_data = ItemCreate(name="New Item", description="New Description")
    created_item = await item_service.create_item(new_item_data)
    assert created_item is not None
    assert created_item.name == "New Item"
    assert created_item.description == "New Description"
    assert created_item.id == 3  # Assuming 2 items initially in mock_db
    assert mock_db[3]["name"] == "New Item"

@pytest.mark.asyncio
async def test_update_item_existing(item_service, mock_db):
    update_data = ItemUpdate(name="Updated Name", description="Updated Description")
    updated_item = await item_service.update_item(1, update_data)
    assert updated_item is not None
    assert updated_item.id == 1
    assert updated_item.name == "Updated Name"
    assert updated_item.description == "Updated Description"
    assert mock_db[1]["name"] == "Updated Name"

@pytest.mark.asyncio
async def test_update_item_partial(item_service, mock_db):
    update_data = ItemUpdate(name="Partial Update")
    updated_item = await item_service.update_item(1, update_data)
    assert updated_item is not None
    assert updated_item.id == 1
    assert updated_item.name == "Partial Update"
    assert updated_item.description == "Description 1" # Description should remain unchanged

@pytest.mark.asyncio
async def test_update_item_non_existing(item_service):
    update_data = ItemUpdate(name="Non Existent")
    updated_item = await item_service.update_item(999, update_data)
    assert updated_item is None

@pytest.mark.asyncio
async def test_delete_item_existing(item_service, mock_db):
    deleted = await item_service.delete_item(1)
    assert deleted is True
    assert 1 not in mock_db

@pytest.mark.asyncio
async def test_delete_item_non_existing(item_service, mock_db):
    deleted = await item_service.delete_item(999)
    assert deleted is False
    assert len(mock_db) == 2 # Ensure no items were deleted
