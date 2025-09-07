import asyncio
from typing import List, Dict, Optional

from ..models.schemas import Item, ItemCreate, ItemUpdate


class ItemService:
    def __init__(self, db: Dict[int, dict]):
        self.db = db

    async def get_items(self) -> List[Item]:
        await asyncio.sleep(0)
        return [Item(**item) for item in self.db.values()]

    async def get_item(self, item_id: int) -> Optional[Item]:
        await asyncio.sleep(0)
        if item_id in self.db:
            return Item(**self.db[item_id])
        return None

    async def create_item(self, item: ItemCreate) -> Item:
        await asyncio.sleep(0)
        new_id = max(self.db.keys(), default=0) + 1
        new_item = Item(id=new_id, **item.model_dump())
        self.db[new_id] = new_item.model_dump()
        return new_item

    async def update_item(self, item_id: int, item: ItemUpdate) -> Optional[Item]:
        await asyncio.sleep(0)
        if item_id not in self.db:
            return None
        current_item_data = self.db[item_id]
        update_data = item.model_dump(exclude_unset=True)
        current_item_data.update(update_data)
        self.db[item_id] = current_item_data
        return Item(**current_item_data)

    async def delete_item(self, item_id: int) -> bool:
        await asyncio.sleep(0)
        if item_id in self.db:
            del self.db[item_id]
            return True
        return False
