import logging
import os
import aiohttp
from discord.ext import commands

PRILOG_TOKEN = os.environ["PRILOG_TOKEN"]


class PriLog(commands.Cog):
    """Prilog APIを利用します。"""

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord.PriLog')

    async def get_response(self, url):
        async with aiohttp.CliantSession() as session:
            async with session.get('https://prilog.jp/rest/analyze'
                                   f'?Url={url}&Token={PRILOG_TOKEN}') as r:
                try:
                    return await r.json()
                except Exception:
                    return None

    @commands.command()
    async def log(self, ctx, url: str):
        """
        引数にクランバトル動画を渡すとPriLogを利用できます。
        コマンドとURLの間に半角スペースを空けてください。
        例: /log https://www.youtube.com/watch?v=mvLSw5vCpGU
        """
        resp = await self.get_response(url)
        if resp:
            await ctx.send(resp['timeline_txt'])
            status = resp['status']
            self.logger.info(f'Try to get:{url}... status={status}')
        else:
            self.logger.error('failed to get respons from PriLog')


def setup(bot):
    bot.add_cog(PriLog(bot))
