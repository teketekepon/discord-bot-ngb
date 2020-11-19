# -*- coding: utf-8 -*-

from itertools import zip_longest
import time
import threading
import pickle

import discord
from discord.ext import commands

from .lib.dbox import TransferData

TEMP_PATH = r'./tmp/'
# 10月のボス
BOSSES = [
    'ゴブリングレート',
    'ライライ',
    'オークチーフ',
    'オブシダンワイバーン',
    'レサトパルト'
]


class Reserve(commands.Cog):
    """
    ボスの凸希望を管理します。
    各メンバー1つまで凸を希望するボスを/(ボス名) (備考)コマンドで登録します。
    例: /ワイバーン 物理1000万
    """

    def __init__(self, bot):
        self.bot = bot
        # ボスごとの予約者 {key = user.id(int) value = name + note(str)}
        self.res = {}

        self.rev = TransferData().download_file(r'/res.pkl',
                                                TEMP_PATH + 'res.pkl')
        if self.rev is not None:
            with open(TEMP_PATH + 'res.pkl', 'rb') as f:
                items = pickle.load(f)
            if any(True for _ in items):
                for x, i in enumerate(items):
                    # Noneを除外し辞書に追加
                    self.res[x].update(list(filter(None, i)))
        th = threading.Thread(target=self.second_download)
        th.setDaemon(True)
        th.start()

    def second_download(self):
        time.sleep(120)
        tmp = TransferData().download_file(r'/res.pkl', TEMP_PATH + 'res.pkl')
        if self.rev is not None and tmp is not None and self.rev != tmp:
            with open(TEMP_PATH + 'res.pkl', 'rb') as f:
                self.res = pickle.load(f)

    def cog_unload(self):
        """シャットダウン時に変数をDropboxへ保存"""
        items = zip_longest(self.res[0].items(), self.res[1].items(),
                            self.res[2].items(), self.res[3].items(),
                            self.res[4].items())
        with open(TEMP_PATH + 'res.pkl', 'wb') as f:
            pickle.dump(items, f)
        TransferData().upload_file(TEMP_PATH + 'res.pkl', r'/res.pkl')

    def overlap_check(self, user_id):
        """すでに予約しているユーザーをはじく"""
        union_key = self.res[0].keys() | self.res[1].keys() | \
            self.res[2].keys() | self.res[3].keys() | self.res[4].keys()
        for i in union_key:
            if user_id == i:
                return True
        return False

    def overlap_check_tri(self, user_id):
        """すでに"3つ"予約しているユーザーをはじく"""
        n = 0
        if user_id in self.res[0]:
            n += 1
        if user_id in self.res[1]:
            n += 1
        if user_id in self.res[2]:
            n += 1
        if user_id in self.res[3]:
            n += 1
        if user_id in self.res[4]:
            n += 1
        if n >= 3:
            return True
        return False

    @commands.command(aliases=['予約', '凸予約', '予定'])
    async def yoyaku(self, ctx):  # 予約内容の確認
        """
        各ボスを希望するメンバー一覧をチャットします。
        /予約 /凸予約 /予定 でも反応します。
        """
        embed = discord.Embed(title='**現在の凸希望者**', color=0x0000ff)
        embed.add_field(name=f'{BOSSES[0]}',
                        value='まだ誰もいません' if not self.res[0]
                        else ', '.join(self.res[0].values()), inline=False)
        embed.add_field(name=f'{BOSSES[1]}',
                        value='まだ誰もいません' if not self.res[1]
                        else ', '.join(self.res[1].values()), inline=False)
        embed.add_field(name=f'{BOSSES[2]}',
                        value='まだ誰もいません' if not self.res[2]
                        else ', '.join(self.res[2].values()), inline=False)
        embed.add_field(name=f'{BOSSES[3]}',
                        value='まだ誰もいません' if not self.res[3]
                        else ', '.join(self.res[3].values()), inline=False)
        embed.add_field(name=f'{BOSSES[4]}',
                        value='まだ誰もいません' if not self.res[4]
                        else ', '.join(self.res[4].values()), inline=False)
        await ctx.send(embed=embed)

    @commands.command(name=BOSSES[0], aliases=['b1', 'boss1'])
    async def res1(self, ctx, note=''):
        """1体目のボスを希望するコマンド /b1 /boss1でも反応します"""
        if self.overlap_check(ctx.author.id):
            await ctx.send('予約はひとり1つまでです。')
            return
        self.res[0][ctx.author.id] = ctx.author.display_name if not note\
            else ctx.author.display_name + f': {note}'

    @commands.command(name=BOSSES[1], aliases=['b2', 'boss2'])
    async def res2(self, ctx, note=''):
        """2体目のボスを希望するコマンド /b2 /boss2でも反応します"""
        if self.overlap_check(ctx.author.id):
            await ctx.send('予約はひとり1つまでです。')
            return
        self.res[1][ctx.author.id] = ctx.author.display_name if not note\
            else ctx.author.display_name + f': {note}'

    @commands.command(name=BOSSES[2], aliases=['b3', 'boss3'])
    async def res3(self, ctx, note=''):
        """3体目のボスを希望するコマンド /b3 /boss3でも反応します"""
        if self.overlap_check(ctx.author.id):
            await ctx.send('予約はひとり1つまでです。')
            return
        self.res[2][ctx.author.id] = ctx.author.display_name if not note\
            else ctx.author.display_name + f': {note}'

    @commands.command(name=BOSSES[3], aliases=['b4', 'boss4'])
    async def res4(self, ctx, note=''):
        """4体目のボスを希望するコマンド /b4 /boss4でも反応します"""
        if self.overlap_check(ctx.author.id):
            await ctx.send('予約はひとり1つまでです。')
            return
        self.res[3][ctx.author.id] = ctx.author.display_name if not note\
            else ctx.author.display_name + f': {note}'

    @commands.command(name=BOSSES[4], aliases=['b5', 'boss5'])
    async def res5(self, ctx, note=''):
        """5体目のボスを希望するコマンド /b5 /boss5でも反応します"""
        if self.overlap_check(ctx.author.id):
            await ctx.send('予約はひとり1つまでです。')
            return
        self.res[4][ctx.author.id] = ctx.author.display_name if not note\
            else ctx.author.display_name + f': {note}'

    @commands.command(aliases=['凸完了', '完了', 'クリア'])
    async def clear(self, ctx):  # 予約を削除
        """
        実行したユーザーの凸希望を削除します。
        /凸完了 /完了 /クリア でも反応します。
        """
        if ctx.author.id in self.res[0]:
            del self.res[0][ctx.author.id]
        if ctx.author.id in self.res[1]:
            del self.res[1][ctx.author.id]
        if ctx.author.id in self.res[2]:
            del self.res[2][ctx.author.id]
        if ctx.author.id in self.res[3]:
            del self.res[3][ctx.author.id]
        if ctx.author.id in self.res[4]:
            del self.res[4][ctx.author.id]


# Bot本体側からコグを読み込む際に呼び出される関数。
def setup(bot):
    bot.add_cog(Reserve(bot))
