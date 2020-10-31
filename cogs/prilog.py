import logging
import os
import aiohttp
from discord.ext import commands

PRILOG_TOKEN = os.environ["PRILLOG_TOKEN"]


class PriLog(commands.Cog):
    """Prilog APIを利用するためのコグ"""

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord.PriLog')

    async def get_response(self, url):
        async with aiohttp.CliantSession() as session:
            async with session.get('https://prilog.jp/rest/analyze'
                                   f'?Url={url}&Token={PRILOG_TOKEN}') as r:
                self.logger.info(f'Try to get:{url}... status={r.status}')
                try:
                    return await r.json()
                except Exception:
                    return None

    @commands.command()
    async def log(self, ctx, url: str):
        resp = self.get_response(url)
        if resp:
            await ctx.send(resp['timeline_txt'])


def setup(bot):
    bot.add_cog(PriLog(bot))
