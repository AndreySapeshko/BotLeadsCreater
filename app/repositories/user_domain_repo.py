from datetime import datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.db.models import Domain, UserDomain, UserDomainStatus
from app.db.session import AsyncSessionLocal


class UserDomainRepo:

    async def filter_new_domains(
        self, session: AsyncSessionLocal, user_id, domains: list[str], domain_ids: dict[str, str]
    ) -> list[str]:
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

        res = await session.execute(q)
        return [row[0] for row in res.fetchall()]

    async def upsert_leads(self, session: AsyncSessionLocal, user_id, domains: list[str], status: str):
        if not domains:
            return

        # получаем id доменов
        q = select(Domain.id, Domain.domain).where(Domain.domain.in_(domains))
        res = await session.execute(q)
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
        await session.execute(stmt)
        await session.commit()

    async def get_leads_by_user(self, session: AsyncSessionLocal, user_id):
        stmt = (
            select(Domain, UserDomain)
            .join(UserDomain, UserDomain.domain_id == Domain.id)
            .where(UserDomain.user_id == user_id, UserDomain.status == UserDomainStatus.LEAD)
        )

        res = await session.execute(stmt)

        return [
            {
                "domain": domain.domain,
                "user_domain_id": user_domain.id,
            }
            for domain, user_domain in res.all()
        ]

    async def set_status(self, session: AsyncSessionLocal, user_domain_id: int, status: str):
        if status not in UserDomainStatus._value2member_map_:
            return False

        user_domain = await session.get(UserDomain, user_domain_id)
        if user_domain:
            user_domain.status = status
            await session.commit()
            return True
        return False

    async def get_contacted_leads_by_user(self, session, user_id):
        stmt = (
            select(Domain, UserDomain)
            .join(UserDomain, UserDomain.domain_id == Domain.id)
            .where(UserDomain.user_id == user_id, UserDomain.status == UserDomainStatus.CONTACTED)
        )

        res = await session.execute(stmt)

        return [
            {
                "domain": domain.domain,
                "user_domain_id": user_domain.id,
            }
            for domain, user_domain in res.all()
        ]


user_domain_repo = UserDomainRepo()
