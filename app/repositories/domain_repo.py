from datetime import datetime

from sqlalchemy.dialects.postgresql import insert

from app.db.models import Domain
from app.db.session import AsyncSessionLocal
from app.utils.url_norm import normalize_domain


class DomainRepo:

    async def upsert_many(self, session: AsyncSessionLocal, domains: list[str], seen_at: datetime) -> dict[str, str]:
        """
        Вставляет новые домены, обновляет last_seen у существующих.
        Возвращает mapping: domain -> domain_id
        """
        norm_domains = {normalize_domain(d) for d in domains if d and normalize_domain(d)}

        if not norm_domains:
            return {}

        rows = [{"domain": d, "first_seen": seen_at, "last_seen": seen_at} for d in set(norm_domains)]

        stmt = insert(Domain).values(rows)
        stmt = stmt.on_conflict_do_update(
            index_elements=[Domain.domain],
            set_={"last_seen": seen_at},
        ).returning(Domain.id, Domain.domain)

        res = await session.execute(stmt)
        return {domain: str(id_) for id_, domain in res.fetchall()}
