import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from datetime import datetime
import psutil
import logging

from bot import bot
from Sentry.webhook import sentry_router

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # # Startup: Discord 봇 시작
    # try:
    #     await asyncio.create_task(bot.start(bot.token))
    #     logger.info("Starting Discord bot...")
    # except Exception as e:
    #     logger.error(f"Failed to start bot: {e}")
    #     raise

    # yield  # FastAPI 애플리케이션 실행 

    # # Shutdown: Discord 봇 종료
    # try:
    #     await bot.close()
    #     logger.info("Discord bot closed")
    # except Exception as e:
    #     logger.error(f"Error closing bot: {e}")
    bot_task = asyncio.create_task(bot.start(bot.token))
    logger.info("Starting Discord bot...")
    yield
    await bot.close()
    logger.info("Discord bot closed")

# FastAPI 앱 생성 (전역 변수로 다른 모듈에서 접근 가능)
app = FastAPI(
    title="Gitfolio Discord Bot",
    description="Gitfolio 프로젝트를 위한 디스코드 봇",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "FastAPI Server"
    }

@app.get("/health/detailed")
async def detailed_health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "FastAPI Server",
        "system_stats": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent
        }
    }

# Sentry 웹훅 라우터 등록
app.include_router(sentry_router)

async def start_bot():
    try:
        logger.info("Starting Discord bot...")
        await bot.start(bot.token)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

def run_bot():
    logger.info("Starting FastAPI server and Discord bot..")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    bot_task = loop.create_task(start_bot())

    config = uvicorn.Config(
        app,
        host=bot.host,
        port=bot.port,
        reload=False
    )

    server = uvicorn.Server(config)

    try:
        loop.run_until_complete(server.serve())
    except KeyboardInterrupt:
        logger.info("Shutting down bot and server...")
        loop.run_until_complete(bot.close())
    finally:
        loop.close()

if __name__ == "__main__":
    # run_bot()
    uvicorn.run(app, host=bot.host, port=bot.port)