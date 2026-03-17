import pytest
from uuid6 import uuid7

from arclith.application.use_cases.create import CreateUseCase
from arclith.application.use_cases.delete import DeleteUseCase
from arclith.application.use_cases.duplicate import DuplicateUseCase
from tests.units.conftest import DummyEntity


async def test_duplicate_assigns_new_uuid(repo, logger):
    entity = await CreateUseCase(repo, logger).execute(DummyEntity(name="original"))
    clone = await DuplicateUseCase(repo, logger).execute(entity.uuid)
    assert clone.uuid != entity.uuid
    assert clone.name == "original"


async def test_duplicate_stores_clone(repo, logger):
    entity = await CreateUseCase(repo, logger).execute(DummyEntity())
    clone = await DuplicateUseCase(repo, logger).execute(entity.uuid)
    assert await repo.read(clone.uuid) is not None


async def test_duplicate_not_found_raises(repo, logger):
    with pytest.raises(KeyError):
        await DuplicateUseCase(repo, logger).execute(uuid7())


async def test_duplicate_deleted_raises(repo, logger):
    entity = await CreateUseCase(repo, logger).execute(DummyEntity())
    await DeleteUseCase(repo, logger).execute(entity.uuid)
    with pytest.raises(KeyError):
        await DuplicateUseCase(repo, logger).execute(entity.uuid)

