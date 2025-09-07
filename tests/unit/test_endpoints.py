from fastapi.testclient import TestClient
from src.main import app
from unittest.mock import patch
from src.models.schemas import ItemUpdate

client = TestClient(app)

def test_create_item():
    with patch("src.services.item_service.ItemService.create_item") as mock_create_item:
        mock_create_item.return_value = {"id": 3, "name": "New Item", "description": "A new item"}
        response = client.post("/api/v1/items", json={"name": "New Item", "description": "A new item"})
        assert response.status_code == 201
        assert response.json() == {"id": 3, "name": "New Item", "description": "A new item"}
        mock_create_item.assert_called_once()

def test_read_item_not_found():
    with patch("src.services.item_service.ItemService.get_item") as mock_get_item:
        mock_get_item.return_value = None
        response = client.get("/api/v1/items/999")
        assert response.status_code == 404
        assert response.json() == {"detail": "Item not found"}
        mock_get_item.assert_called_once_with(item_id=999)

def test_read_items():
    with patch("src.services.item_service.ItemService.get_items") as mock_get_items:
        mock_get_items.return_value = [{"id": 1, "name": "Item 1", "description": "Desc 1"}]
        response = client.get("/api/v1/items")
        assert response.status_code == 200
        assert response.json() == [{"id": 1, "name": "Item 1", "description": "Desc 1"}]
        mock_get_items.assert_called_once()

def test_read_item_found():
    with patch("src.services.item_service.ItemService.get_item") as mock_get_item:
        mock_get_item.return_value = {"id": 1, "name": "Found Item", "description": "Found Description"}
        response = client.get("/api/v1/items/1")
        assert response.status_code == 200
        assert response.json() == {"id": 1, "name": "Found Item", "description": "Found Description"}
        mock_get_item.assert_called_once_with(item_id=1)

def test_update_item():
    with patch("src.services.item_service.ItemService.update_item") as mock_update_item:
        mock_update_item.return_value = {"id": 1, "name": "Updated Item", "description": "Updated Description"}
        response = client.put("/api/v1/items/1", json={"name": "Updated Item", "description": "Updated Description"})
        assert response.status_code == 200
        assert response.json() == {"id": 1, "name": "Updated Item", "description": "Updated Description"}
        mock_update_item.assert_called_once_with(1, ItemUpdate(name="Updated Item", description="Updated Description"))

def test_update_item_not_found():
    with patch("src.services.item_service.ItemService.update_item") as mock_update_item:
        mock_update_item.return_value = None
        response = client.put("/api/v1/items/999", json={"name": "Non Existent"})
        assert response.status_code == 404
        assert response.json() == {"detail": "Item not found"}
        mock_update_item.assert_called_once_with(999, ItemUpdate(name="Non Existent"))

def test_delete_item():
    with patch("src.services.item_service.ItemService.delete_item") as mock_delete_item:
        mock_delete_item.return_value = True
        response = client.delete("/api/v1/items/1")
        assert response.status_code == 204
        mock_delete_item.assert_called_once_with(1)

def test_delete_item_not_found():
    with patch("src.services.item_service.ItemService.delete_item") as mock_delete_item:
        mock_delete_item.return_value = False
        response = client.delete("/api/v1/items/999")
        assert response.status_code == 404
        assert response.json() == {"detail": "Item not found"}
        mock_delete_item.assert_called_once_with(999)