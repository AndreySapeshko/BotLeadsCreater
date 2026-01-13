from sqlalchemy import select

from app.db.models import Query


class QueryRepo:
    def __init__(self, session):
        self.session = session

    async def get_active(self, user_id, business_type: str):
        q = (
            select(Query)
            .where(Query.user_id == user_id)
            .where(Query.business_type == business_type)
            .where(Query.active.is_(True))
        )
        res = await self.session.execute(q)
        return res.scalars().all()
