from sqlalchemy import select

from app.db.models import Query
from app.db.session import AsyncSessionLocal


class QueryRepo:

    async def get_active(self, user_id, business_type: str):
        async with AsyncSessionLocal() as session:
            q = (
                select(Query)
                .where(Query.user_id == user_id)
                .where(Query.business_type == business_type)
                .where(Query.active.is_(True))
            )
            res = await session.execute(q)
        return res.scalars().all()

    async def get_queries_by_user_id(self, user_id):
        async with AsyncSessionLocal() as session:
            stmt = select(Query).where(Query.user_id == user_id)
            return (await session.execute(stmt)).scalars().all()

    async def list_business_types(self, user_id):
        queries = await self.get_queries_by_user_id(user_id)
        niches = []
        for query in queries:
            if query.business_type not in niches:
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
        async with AsyncSessionLocal() as session:
            stmt = select(Query).where(Query.user_id == user_id, Query.business_type == niche)
            queries = (await session.execute(stmt)).scalars().all()

            existing_phrases = [q.search_phrase for q in queries]

            for phrase in phrases:
                phrase = phrase.strip()
                if phrase not in existing_phrases:
                    query = Query(user_id=user_id, business_type=niche, search_phrase=phrase)
                    session.add(query)
            await session.commit()

    async def delete_queries(self, user_id, niche, removed_phrases):
        removed = [p.strip() for p in removed_phrases if p and p.strip()]
        if not removed:
            return []
        async with AsyncSessionLocal() as session:
            stmt = select(Query).where(Query.user_id == user_id, Query.business_type == niche)
            queries = (await session.execute(stmt)).scalars().all()

            existing_phrases = [q.search_phrase for q in queries]
            non_existent_phrases = [p for p in removed if p not in existing_phrases]
            queries_to_remove = [q for q in queries if q.search_phrase in removed]

            for query in queries_to_remove:
                await session.delete(query)
            await session.commit()

        return non_existent_phrases

    async def delete_niche(self, user_id, niche):
        async with AsyncSessionLocal() as session:
            stmt = select(Query).where(Query.user_id == user_id, Query.business_type == niche)
            queries = (await session.execute(stmt)).scalars().all()
            if queries:
                for query in queries:
                    await session.delete(query)
                await session.commit()
                return True
            return False


query_repo = QueryRepo()
