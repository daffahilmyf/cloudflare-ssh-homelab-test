from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict

from ...models.schemas import Item, ItemCreate, ItemUpdate
from ...services.item_service import ItemService
from ...db.session import get_db

router = APIRouter()


def get_item_service(db: Dict = Depends(get_db)) -> ItemService:
    return ItemService(db)


@router.get("/items", response_model=List[Item])
async def read_items(service: ItemService = Depends(get_item_service)):
    return await service.get_items()


@router.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: ItemCreate, service: ItemService = Depends(get_item_service)
):
    return await service.create_item(item)


@router.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int, service: ItemService = Depends(get_item_service)):
    db_item = await service.get_item(item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return db_item


@router.put("/items/{item_id}", response_model=Item)
async def update_item(
    item_id: int, item: ItemUpdate, service: ItemService = Depends(get_item_service)
):
    updated_item = await service.update_item(item_id, item)
    if updated_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return updated_item


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int, service: ItemService = Depends(get_item_service)):
    deleted = await service.delete_item(item_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return
