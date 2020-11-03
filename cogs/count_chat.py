import logging
import pickle
from datetime import datetime
import discord
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
        self.i = 0
        self.bot = bot
        # work_channels {channel.id:[count, message.id]}
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
            pickle.dump(self.work_channels, f)
        TransferData().upload_file(TEMP_PATH + 'chat.pkl', r'/chat.pkl')
        self.logger.info('Pickle saved')
        self.chat.cancel()

    @commands.command()
    async def chat_start(self, ctx):
        """このコマンドを実行したチャンネルでチャットカウントを実行します"""
        if ctx.channel.id in self.work_channels.keys():
            await ctx.send('このチャンネルではすでにカウントが行われています')
        else:
            self.work_channels[ctx.channel.id] = [0, 0]
            await ctx.send('このチャンネルでのカウントを開始します')

    @commands.command()
    async def chat_stop(self, ctx):
        """このコマンドを実行したチャンネルでチャットカウントを停止します"""
        if ctx.channel.id in self.work_channels.keys():
            del self.work_channels[ctx.channel.id]
            await ctx.send('このチャンネルでのカウントを停止しました')
        else:
            await ctx.send('このチャンネルではカウントが行われていません')

    @commands.command()
    async def count(self, ctx):
        """このコマンドを実行したチャンネルのその日のリアクション数から、残り凸数を数えます"""
        if (ctx.channel.id not in self.work_channels.keys()
                or 0 in self.work_channels[ctx.channel.id]):
            await ctx.send('このチャンネルはカウントチャンネルではないか、'
                           'まだメッセージを作成していません。')
            return
        msg = await ctx.channel.fetch_message(self.work_channels
                                              [ctx.channel.id][1])
        totu = 96
        for reactions in msg.reactions:
            for i, emoji in enumerate(EMOJI):
                if reactions.emoji == emoji:
                    totu -= reactions.count * (3-i)
        await ctx.send(f'残り{totu}凸')

    @commands.command()
    async def count_users(self, ctx):
        """
        このコマンドを実行したチャンネルのその日のリアクションしたユーザーを集計します
        """
        if (ctx.channel.id not in self.work_channels.keys()
                or 0 in self.work_channels[ctx.channel.id]):
            await ctx.send('このチャンネルはカウントチャンネルではないか、'
                           'まだメッセージを作成していません。')
            return
        msg = await ctx.channel.fetch_message(self.work_channels
                                              [ctx.channel.id][1])
        embed = discord.Embed(title='凸状況')
        count = 0
        display_name = []
        for reactions in msg.reactions:
            for emoji in EMOJI:
                if reactions.emoji == emoji:
                    users = await reactions.users().flatten()
                    for user in users:
                        if user.bot:
                            continue
                        display_name.append(user.display_name)
                    embed.add_field(name=f'残り{count}凸',
                                    value=', '.join(display_name))

    @tasks.loop(seconds=60)
    async def chat(self):
        # now = datetime.now().strftime('%H:%M')
        # if now == '05:00':
        if self.i < 3:
            for i in self.work_channels.keys():
                self.work_channels[i][0] += 1
                channel = self.bot.get_channel(i)
                try:
                    msg = await channel.send(f'{self.work_channels[i][0]} 日目開始！\n'
                                             'このチャットにリアクションを追加して、残凸数を教えてください♪')
                except AttributeError:
                    return
                for emoji in EMOJI:
                    await msg.add_reaction(emoji)
                self.work_channels[i][1] = msg.id
        self.i += 1


def setup(bot):
    bot.add_cog(CountChat(bot))
