from discord import Intents, Game, Status, Object, HTTPException
from discord.ext import commands
import logging

from settings import settings

# 로깅 설정
logger = logging.getLogger(__name__)

# Discord 봇 설정
intents = Intents.default()
intents.message_content = True
intents.members = True

class DiscordBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",                              # 명령어 접두사 설정
            intents=intents.all(),                           # 모든 권한 활성화
            sync_command=True,
            application_id=settings.DISCORD_BOT_ID    # 봇 ID
        )
        self.initial_extensions = [
            "Sentry.command"
        ]
        self.server_id = settings.DISCORD_SERVER_ID
        self.id = settings.DISCORD_BOT_ID
        self.token = settings.DISCORD_BOT_TOKEN
        self.sentry_channel = settings.DISCORD_SENTRY_CHANNEL_ID
        self.host = settings.HOST
        self.port = settings.PORT

    async def setup_hook(self):
        if not self.sentry_channel:
            try:
                self.sentry_channel = await self.fetch_channel(self.sentry_channel)
                logger.info(f"Successfully connected to channel {self.sentry_channel}")
            except HTTPException as e:
                logger.error(f"Error: Could not find channel with ID {self.sentry_channel}: {e}")

        for ext in self.initial_extensions:
            await self.load_extension(ext)
            
        await self.tree.sync(guild=Object(id=self.server_id))

    async def on_ready(self):
        """봇이 준비되었을 때 호출되는 이벤트"""
        logger.info(f'Logged in as {self.user.name} (ID: {self.user.id})')
        logger.info(f'Connected to {len(self.guilds)} guilds')
        self.channel = self.get_channel(self.sentry_channel)
        
        activity = Game("조일민 탈영병 추노")
        await self.change_presence(status=Status.online, activity=activity)

# 봇 인스턴스 생성 (전역 변수로 다른 모듈에서 접근 가능)
bot = DiscordBot()