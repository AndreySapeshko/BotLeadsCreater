import asyncio
import logging
import logging.config

from aiogram import Bot, Dispatcher

from app.bot.handlers import router
from app.config import SERPER_KEY, TELEGRAM_BOT_TOKEN
from app.integrations.http_fetch import HtmlFetcher
from app.integrations.serper import SerperClient
from app.llm.llm_stage import LLMStage
from app.llm.open_router_client import get_open_router_client
from app.logging_config import LOGGING_CONFIG
from app.repositories.domain_repo import DomainRepo
from app.repositories.query_repo import query_repo
from app.repositories.search_cache_repo import SearchCacheRepo
from app.repositories.user_domain_repo import user_domain_repo
from app.services.pipeline_service import PipelineService

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

openrouter_llm = get_open_router_client()
llm_stage = LLMStage(openrouter_llm)

serper = SerperClient(SERPER_KEY)
fetcher = HtmlFetcher()

domain_repo = DomainRepo()
search_cache_repo = SearchCacheRepo()

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
    print(f"🤖 Bot service started bot token: {TELEGRAM_BOT_TOKEN[:15]}")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


def run():
    asyncio.run(main())


if __name__ == "__main__":
    run()
