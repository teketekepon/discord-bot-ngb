import logging
import pickle
from datetime import datetime
# import discord
from discord.ext import tasks, commands

from cogs.lib.dbox import TransferData

TEMP_PATH = r'./tmp/'
EMOJI = ['0️⃣', '1️⃣', '2️⃣']


class CountChat(commands.Cog):
    """
    チャット形式で残凸管理を行う。
    /chat_startコマンドを実行したチャンネル上で、朝5時にbotがコメントする。
    このコメントにリアクションをつけることで残凸数を把握する。
    """
    def __init__(self, bot):
        self.bot = bot
        self.work_channels = {}
        self.logger = logging.getLogger('discord.CountChat')
        r = TransferData().download_file(r'/chat.pkl',
                                         TEMP_PATH + 'chat.pkl')
        if r is not None:
            with open(TEMP_PATH + 'chat.pkl', 'rb') as f:
                self.work_channels = pickle.load(f)
                self.logger.info('Pickle loaded')
        self.chat.start()

    def cog_unload(self):
        """シャットダウン時に変数をDropboxへ保存"""
        with open(TEMP_PATH + 'chat.pkl', 'wb') as f:
            pickle.dump(self.chat, f)
        TransferData().upload_file(TEMP_PATH + 'chat.pkl', r'/chat.pkl')
        self.logger.info('Pickle saved')
        self.chat.cancel()

    @commands.command()
    async def chat_start(self, ctx):
        """このコマンドを実行したチャンネルでチャットカウントを実行します"""
        if ctx.channel.id in self.work_channels.keys():
            await ctx.send('このチャンネルではすでにカウントが行われています')
        else:
            self.work_channels[ctx.channel.id] = 0
            await ctx.send('このチャンネルでのカウントを開始します')

    @commands.command()
    async def chat_stop(self, ctx):
        """このコマンドを実行したチャンネルでチャットカウントを停止します"""
        if ctx.channel.id in self.work_channels.keys():
            del self.work_channels[ctx.channel.id]
            await ctx.send('このチャンネルでのカウントを停止しました')
        else:
            await ctx.send('このチャンネルではカウントが行われていません')

    @tasks.loop(seconds=60)
    async def chat(self):
        now = datetime.now().strftime('%H:%M')
        self.logger.info(now)
        if now == '05:00':
            for i in self.work_channels.keys():
                self.work_channels[i] += 1
                msg = await i.send(f'{self.work_channels[i]} 日目開始！\n'
                                   'このチャットにリアクションを追加して、残凸数を教えてください♪')
                for emoji in EMOJI:
                    await msg.reaction.add(emoji)


def setup(bot):
    bot.add_cog(CountChat(bot))
