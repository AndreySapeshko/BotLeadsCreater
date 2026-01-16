from datetime import datetime

from app.db.session import AsyncSessionLocal
from app.integrations.http_fetch import HtmlFetcher
from app.integrations.serper import SerperClient
from app.utils.html_signals import extract_signals
from app.utils.url_norm import normalize_domain


class PipelineService:
    def __init__(
        self,
        serper: SerperClient,
        fetcher: HtmlFetcher,
        query_repo,
        domain_repo,
        search_cache_repo,
        user_domain_repo,
        llm_stage,  # позже
    ):
        self.serper = serper
        self.fetcher = fetcher
        self.query_repo = query_repo
        self.domain_repo = domain_repo
        self.search_cache_repo = search_cache_repo
        self.user_domain_repo = user_domain_repo
        self.llm_stage = llm_stage

    async def run(
        self, session: AsyncSessionLocal, user_id, business_type: str, max_results_per_query: int = 10
    ) -> dict:
        queries = await self.query_repo.get_active(user_id=user_id, business_type=business_type)
        if not queries:
            return {"status": "no_queries"}

        # 1) Search + cache
        candidates: list[tuple] = []  # (query_id, domain, source_url, rank)
        seen_at = datetime.utcnow()

        for q in queries:
            organic = await self.serper.search(q.search_phrase, num=max_results_per_query)
            for i, item in enumerate(organic, start=1):
                url = item.get("link") or ""
                dom = normalize_domain(url)
                if not dom:
                    continue
                candidates.append((q.id, dom, url, i))

        # 2) Upsert domains + write search_cache
        # domain_repo должен вернуть mapping domain->domain_id
        domain_ids = await self.domain_repo.upsert_many(session, [c[1] for c in candidates], seen_at=seen_at)
        await self.search_cache_repo.upsert_many(
            session,
            [
                {"query_id": qid, "domain_id": domain_ids[dom], "seen_at": seen_at, "rank": rank}
                for (qid, dom, url, rank) in candidates
            ],
        )

        # 3) Filter: only domains not yet seen by this user
        uniq_domains = list({c[1] for c in candidates})
        new_domain_ids = await self.user_domain_repo.filter_new_domains(
            session=session, user_id=user_id, domains=uniq_domains, domain_ids=domain_ids
        )
        # new_domain_ids: list of domain strings or ids — как решишь в репо

        # 4) Fetch + analyze
        leads = []
        for dom in new_domain_ids:
            url = f"https://{dom}"
            try:
                html = await self.fetcher.fetch(url)
            except Exception:
                # можно пометить как failed_fetch
                continue

            sig = extract_signals(dom, html)
            print(
                f"sig['has_form']: {sig["has_form"]}, sig['has_telegram']: {sig["has_telegram"]}"
                f", sig['has_chat']: {sig["has_chat"]}"
            )
            # v1 фильтр
            if sig["has_form"] and (not sig["has_telegram"]):
                leads.append(sig)

        # 5) LLM stage (пока заглушка)
        enriched = await self.llm_stage.enrich(leads) if self.llm_stage else leads

        # 6) Save user_domain leads
        await self.user_domain_repo.upsert_leads(
            session=session, user_id=user_id, domains=[x["domain"] for x in enriched], status="lead"
        )

        return {
            "status": "ok",
            "queries": len(queries),
            "found_domains": len(uniq_domains),
            "new_domains": len(new_domain_ids),
            "leads": len(enriched),
        }
