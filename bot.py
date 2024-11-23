import os
from discord import Intents, Game, Status, Object, HTTPException
from discord.ext import commands
from discord.gateway import DiscordWebSocket
import logging
from aiohttp import ClientSession, TCPConnector

# from settings import settings

# 로깅 설정
logger = logging.getLogger(__name__)

# Discord 봇 설정
intents = Intents.default()
intents.message_content = True
intents.members = True

class ProxyWebSocket(DiscordWebSocket):
    async def connect(self, *, compression: bool = False) -> None:
        self.proxy = self.http.proxy
        kwargs = {
            'proxy': self.proxy,
            'proxy_headers': None
        }

        self.comporession = compression
        self.shard_id = self.shard_id or 0
        self.shard_count = self.shard_count or 1

        self.session_id = None
        self.sequence = None
        self._zlib = zlib.decompressobj()
        self._buffer = bytearray()
        self._close_code = None
        self._rate_limiter.reset()

        gateway = await self.http.get_gateway()
        self.gateway = gateway

        self._trace = []

        self._ws = await self.http._session.ws_connect(
            gateway,
            compression=None,
            **kwargs
        )

class DiscordBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",                              # 명령어 접두사 설정
            intents=intents.all(),                           # 모든 권한 활성화
            sync_command=True,
            # application_id=settings.DISCORD_BOT_ID,          # 봇 ID   
            # proxy_url=settings.PROXY_URL
            application_id=os.environ['DISCORD_BOT_ID'],          # 봇 ID
            proxy_url=os.environ['PROXY_URL']
        )
        self.initial_extensions = [
            "Sentry.command"
        ]
        # self.server_id = settings.DISCORD_SERVER_ID
        # self.id = settings.DISCORD_BOT_ID
        # self.token = settings.DISCORD_BOT_TOKEN
        # self.sentry_channel = settings.DISCORD_SENTRY_CHANNEL_ID
        # self.host = settings.HOST
        # self.port = settings.PORT
        # self.proxy_url = settings.PROXY_URL
        self.server_id = int(os.environ['DISCORD_SERVER_ID'])
        self.id = int(os.environ['DISCORD_BOT_ID'])
        self.token = os.environ['DISCORD_BOT_TOKEN']
        self.sentry_channel = int(os.environ['DISCORD_SENTRY_CHANNEL_ID'])
        self.host = os.environ['HOST']
        self.port = int(os.environ['PORT'])
        self.proxy_url = os.environ['PROXY_URL']
        self.ws_class = ProxyWebSocket

    async def setup_hook(self):
        self.session = ClientSession(connector=TCPConnector(
            ssl=False,
            proxy=self.proxy_url,
            force_close=True
        ))
        self.http.proxy = self.proxy_url
        self.http._session = self.session

        self.ws._connection.proxy = self.proxy_url
        
        if not self.channel:
            try:
                self.channel = await self.fetch_channel(self.sentry_channel)
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
        
        activity = Game("조일민 탈영병 추노")
        await self.change_presence(status=Status.online, activity=activity)
    
    async def close(self):
        await self.session.close()
        await super().close()

# 봇 인스턴스 생성 (전역 변수로 다른 모듈에서 접근 가능)
bot = DiscordBot()