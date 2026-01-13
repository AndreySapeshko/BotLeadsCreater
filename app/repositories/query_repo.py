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

    async def get_queries_by_user_id(self, user_id):
        stmt = select(Query).where(Query.user_id == user_id)
        return (await self.session.execute(stmt)).scalars().all()

    async def list_business_types(self, user_id):
        queries = await self.get_queries_by_user_id(user_id)
        niches = []
        for query in queries:
            niches.append(query.business_type)
        return niches

    async def list_queries_by_type(self, user_id, niche):
        queries = await self.get_queries_by_user_id(user_id)
        phrases = []
        for query in queries:
            if query.business_type == niche:
                phrases.append(query.search_phrase)
        return phrases

    async def add_queries_from_list(self, user_id, niche, phrases):
        for phrase in phrases:
            query = Query(user_id=user_id, bisnes_type=niche, search_phrase=phrase)
            self.session.add(query)
        await self.session.commit()
