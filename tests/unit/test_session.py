import pytest
from src.db.session import get_db, fake_db

@pytest.mark.asyncio
async def test_get_db():
    db = await get_db()
    assert db is fake_db
    assert isinstance(db, dict)
    assert 1 in db
    assert "name" in db[1]
