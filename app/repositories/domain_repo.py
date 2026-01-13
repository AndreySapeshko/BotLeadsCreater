from datetime import datetime

from sqlalchemy import insert

from app.db.models import Domain


class DomainRepo:
    def __init__(self, session):
        self.session = session

    async def upsert_many(self, domains: list[str], seen_at: datetime) -> dict[str, str]:
        """
        Вставляет новые домены, обновляет last_seen у существующих.
        Возвращает mapping: domain -> domain_id
        """
        if not domains:
            return {}

        rows = [{"domain": d, "first_seen": seen_at, "last_seen": seen_at} for d in set(domains)]

        stmt = insert(Domain).values(rows)
        stmt = stmt.on_conflict_do_update(
            index_elements=[Domain.domain],
            set_={"last_seen": seen_at},
        ).returning(Domain.id, Domain.domain)

        res = await self.session.execute(stmt)
        return {domain: str(id_) for id_, domain in res.fetchall()}
