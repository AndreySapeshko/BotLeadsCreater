from sqlalchemy import insert

from app.db.models import SearchCache


class SearchCacheRepo:
    def __init__(self, session):
        self.session = session

    async def upsert_many(self, rows: list[dict]):
        """
        rows = [{"query_id":..., "domain_id":..., "seen_at":..., "rank":...}]
        """
        if not rows:
            return

        stmt = insert(SearchCache).values(rows)
        stmt = stmt.on_conflict_do_update(
            index_elements=[SearchCache.query_id, SearchCache.domain_id],
            set_={
                "seen_at": stmt.excluded.seen_at,
                "rank": stmt.excluded.rank,
            },
        )
        await self.session.execute(stmt)
