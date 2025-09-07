# In-memory database

from typing import Dict


# In-memory database
fake_db: Dict[int, Dict] = {
    1: {"id": 1, "name": "First Item", "description": "This is the first item."},
    2: {"id": 2, "name": "Second Item", "description": "This is the second item."},
}


async def get_db():
    return fake_db
