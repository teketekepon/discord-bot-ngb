import logging
import aiohttp
from discord.ext import commands

TOKEN = '7AVMHAykgDwkfwiKUgBueOZnUjd5xtWZkoG2iJC'


class PriLog(commands.Cog):
    """Prilog APIを利用するためのコグ"""

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord.PriLog')

    async def get_response(self, url):
        async with aiohttp.CliantSession() as session:
            async with session.get('https://prilog.jp/rest/analyze'
                                   f'?Url={url}&Token={TOKEN}') as r:
                self.logger.info(f'Try to get:{url}... status={r.status}')
                try:
                    return await r.json()
                except Exception:
                    return None

    @commands.command()
    async def log(self, ctx, url):
        resp = self.get_response(url)
        if resp:
            await ctx.send(resp['timeline_txt'])


def setup(bot):
    bot.add_cog(PriLog(bot))
