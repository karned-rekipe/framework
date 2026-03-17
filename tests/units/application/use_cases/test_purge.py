from datetime import datetime, timedelta, timezone

from arclith.application.use_cases.create import CreateUseCase
from arclith.application.use_cases.purge import PurgeUseCase
from tests.units.conftest import DummyEntity


async def test_purge_skipped_when_retention_none(repo, logger):
    entity = await CreateUseCase(repo, logger).execute(DummyEntity())
    await repo.update(entity.model_copy(update={"deleted_at": datetime.now(timezone.utc)}))
    count = await PurgeUseCase(repo, logger, retention_days=None).execute()
    assert count == 0


async def test_purge_removes_expired(repo, logger):
    entity = await CreateUseCase(repo, logger).execute(DummyEntity())
    old = entity.model_copy(update={"deleted_at": datetime.now(timezone.utc) - timedelta(days=10)})
    await repo.update(old)
    count = await PurgeUseCase(repo, logger, retention_days=7).execute()
    assert count == 1
    assert await repo.read(entity.uuid) is None


async def test_purge_keeps_recent(repo, logger):
    entity = await CreateUseCase(repo, logger).execute(DummyEntity())
    recent = entity.model_copy(update={"deleted_at": datetime.now(timezone.utc) - timedelta(hours=1)})
    await repo.update(recent)
    count = await PurgeUseCase(repo, logger, retention_days=7).execute()
    assert count == 0


async def test_purge_zero_retention_removes_immediately(repo, logger):
    entity = await CreateUseCase(repo, logger).execute(DummyEntity())
    deleted = entity.model_copy(update={"deleted_at": datetime.now(timezone.utc) - timedelta(seconds=1)})
    await repo.update(deleted)
    count = await PurgeUseCase(repo, logger, retention_days=0).execute()
    assert count == 1


async def test_purge_empty_repo(repo, logger):
    count = await PurgeUseCase(repo, logger, retention_days=7).execute()
    assert count == 0

