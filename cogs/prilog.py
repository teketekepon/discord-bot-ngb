import logging
import os
import aiohttp
import discord
from discord.ext import commands

PRILOG_TOKEN = os.environ["PRILOG_TOKEN"]


class PriLog(commands.Cog):
    """Prilog APIを利用します。"""

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord.PriLog')

    async def get_response(self, url):
        async with aiohttp.ClientSession() as session:
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
        self.logger.info(f'Try to get:{url}... status={resp["status"]}')
        if resp["status"] < 310:
            embed = discord.Embed(title=resp["result"]["title"],
                                  discription=resp["msg"],
                                  color=0xe8e8ed)
            name = f'総ダメージ: {resp["result"]["total_damage"]}' if \
                resp["result"]["total_damage"] else '総ダメージ: 不明'
            embed.add_field(name=name,
                            value=f'```{resp["result"]["timeline_txt"]}```')
        else:
            embed = discord.Embed(title='解析失敗',
                                  discription=f'エラーメッセージ: {resp["msg"]}',
                                  color=0xed8ab0)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(PriLog(bot))
