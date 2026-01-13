from datetime import datetime

from sqlalchemy import insert, select

from app.db.models import Domain, UserDomain


class UserDomainRepo:
    def __init__(self, session):
        self.session = session

    async def filter_new_domains(self, user_id, domains: list[str], domain_ids: dict[str, str]) -> list[str]:
        """
        Возвращает список domain (строк), которых ещё нет в user_domains у пользователя
        """
        if not domains:
            return []

        q = (
            select(Domain.domain)
            .join(UserDomain, (UserDomain.domain_id == Domain.id) & (UserDomain.user_id == user_id), isouter=True)
            .where(Domain.domain.in_(domains))
            .where(UserDomain.domain_id.is_(None))
        )

        res = await self.session.execute(q)
        return [row[0] for row in res.fetchall()]

    async def upsert_leads(self, user_id, domains: list[str], status: str):
        if not domains:
            return

        # получаем id доменов
        q = select(Domain.id, Domain.domain).where(Domain.domain.in_(domains))
        res = await self.session.execute(q)
        mapping = {domain: id_ for id_, domain in res.fetchall()}

        rows = [
            {
                "user_id": user_id,
                "domain_id": mapping[d],
                "status": status,
                "first_seen": datetime.utcnow(),
                "last_seen": datetime.utcnow(),
            }
            for d in domains
            if d in mapping
        ]

        stmt = insert(UserDomain).values(rows)
        stmt = stmt.on_conflict_do_update(
            index_elements=[UserDomain.user_id, UserDomain.domain_id],
            set_={
                "status": stmt.excluded.status,
                "last_seen": stmt.excluded.last_seen,
            },
        )
        await self.session.execute(stmt)
