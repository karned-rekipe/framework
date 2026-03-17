from arclith.application.use_cases.create import CreateUseCase
from arclith.application.use_cases.delete import DeleteUseCase
from arclith.application.use_cases.find_all import FindAllUseCase
from tests.units.conftest import DummyEntity


async def test_find_all_returns_active(repo, logger):
    await CreateUseCase(repo, logger).execute(DummyEntity(name="a"))
    await CreateUseCase(repo, logger).execute(DummyEntity(name="b"))
    result = await FindAllUseCase(repo, logger).execute()
    assert len(result) == 2


async def test_find_all_excludes_deleted(repo, logger):
    e1 = await CreateUseCase(repo, logger).execute(DummyEntity(name="a"))
    await CreateUseCase(repo, logger).execute(DummyEntity(name="b"))
    await DeleteUseCase(repo, logger).execute(e1.uuid)
    result = await FindAllUseCase(repo, logger).execute()
    assert len(result) == 1
    assert result[0].name == "b"


async def test_find_all_empty(repo, logger):
    assert await FindAllUseCase(repo, logger).execute() == []

