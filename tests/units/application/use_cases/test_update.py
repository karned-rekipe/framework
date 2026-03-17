import asyncio

from arclith.application.use_cases.create import CreateUseCase
from arclith.application.use_cases.update import UpdateUseCase
from tests.units.conftest import DummyEntity


async def test_update_increments_version(repo, logger):
    entity = await CreateUseCase(repo, logger).execute(DummyEntity())
    updated = await UpdateUseCase(repo, logger).execute(entity.model_copy(update={"name": "updated"}))
    assert updated.version == entity.version + 1


async def test_update_refreshes_updated_at(repo, logger):
    entity = await CreateUseCase(repo, logger).execute(DummyEntity())
    before = entity.updated_at
    await asyncio.sleep(0.01)
    updated = await UpdateUseCase(repo, logger).execute(entity)
    assert updated.updated_at >= before


async def test_update_persists_in_repo(repo, logger):
    entity = await CreateUseCase(repo, logger).execute(DummyEntity(name="before"))
    await UpdateUseCase(repo, logger).execute(entity.model_copy(update={"name": "after"}))
    stored = await repo.read(entity.uuid)
    assert stored.name == "after"

