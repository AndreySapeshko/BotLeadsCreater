import asyncio

from aiogram import Bot, Dispatcher

from app.bot.handlers import router
from app.config import SERPER_KEY, TELEGRAM_BOT_TOKEN
from app.db.session import get_session
from app.integrations.http_fetch import HtmlFetcher
from app.integrations.serper import SerperClient
from app.llm.llm_stage import LLMStage
from app.llm.open_router_client import get_open_router_client
from app.repositories.domain_repo import DomainRepo
from app.repositories.query_repo import QueryRepo
from app.repositories.search_cache_repo import SearchCacheRepo
from app.repositories.user_domain_repo import UserDomainRepo
from app.services.pipeline_service import PipelineService

session = get_session()

openrouter_llm = get_open_router_client()
llm_stage = LLMStage(openrouter_llm)

serper = SerperClient(SERPER_KEY)
fetcher = HtmlFetcher()

query_repo = QueryRepo(session)
domain_repo = DomainRepo(session)
search_cache_repo = SearchCacheRepo(session)
user_domain_repo = UserDomainRepo(session)

pipeline = PipelineService(
    serper=serper,
    fetcher=fetcher,
    query_repo=query_repo,
    domain_repo=domain_repo,
    search_cache_repo=search_cache_repo,
    user_domain_repo=user_domain_repo,
    llm_stage=llm_stage,
)

dp = Dispatcher()
bot = Bot(TELEGRAM_BOT_TOKEN)


async def main():

    dp.include_router(router)
    print("🤖 Bot service started")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


def run():
    asyncio.run(main())


if __name__ == "__main__":
    run()
