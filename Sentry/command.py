from discord import app_commands
from discord.ext import commands
from discord import Interaction
from discord import Object
from settings import settings

class command(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="status", description="봇 상태 확인")
    async def staus(self, interaction: Interaction) -> None:
        await interaction.response.send_message("조일민 탈영병 수색 중")

    @app_commands.command(name="검거", description="탈영병 검거")
    async def arrest(self, interaction: Interaction) -> None:
        await interaction.response.send_message("조일민 병장을 계급장 꺾기 형에 처한다!")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(
        command(bot),
        guilds=[Object(id=bot.server_id)]
    )