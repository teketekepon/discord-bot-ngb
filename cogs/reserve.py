# -*- coding: utf-8 -*-
import pickle
import discord
from .dbox import TransferData
from discord.ext import commands
from itertools import zip_longest

TEMP_PATH = r'./tmp/'
# 7月のボス
BOSSES = ['ワイバーン','ランドスロース','ムシュフシュ','ティタノタートル','オルレオン']

class Reserve(commands.Cog):
    """
    ボスの凸希望をディスコード上で管理します。
    各メンバー1つずつ凸を希望するボスを/(ボス名) (備考)コマンドで登録します。
    例: /ワイバーン 物理ワンパン
    """
    # クラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
    # ボスごとの予約者 {key = user.id(int) value = name + note(str)}
    def __init__(self, bot):
        self.bot = bot
        self.res_b1 = {}
        self.res_b2 = {}
        self.res_b3 = {}
        self.res_b4 = {}
        self.res_b5 = {}

        if TransferData().download_file(r'/res.pkl',TEMP_PATH + 'res.pkl'):
            with open(TEMP_PATH + 'res.pkl','rb') as f:
                items = pickle.load(f)
            # zipをアンパック (tuple)
            a, b, c, d, e = zip(*items)
            # Noneを除外しリストに
            self.res_b1.update(list(filter(None,a)))
            self.res_b2.update(list(filter(None,b)))
            self.res_b3.update(list(filter(None,c)))
            self.res_b4.update(list(filter(None,d)))
            self.res_b5.update(list(filter(None,e)))

    def cog_unload(self):
        items = zip_longest(self.res_1.items(), self.res_2.items(),
            self.res_3.items(), self.res_4.items(), self.res_5.items())
        with open(TEMP_PATH + 'res.pkl','wb') as f:
            pickle.dump(items, f)
        TransferData().upload_file(TEMP_PATH + 'res.pkl',r'/res.pkl')

    def overlap_check(self, user_id):  # 重複防止
        union_key = self.res_b1.keys() | self.res_b2.keys() | self.res_b3.keys() |\
            self.res_b4.keys() | self.res_b5.keys()
        for i in union_key:
            if user_id == i:
                return True
        return False

    @commands.command(aliases=['予約','凸予約','予定'])
    async def yoyaku(self, ctx):  # 予約内容の確認
        """
        各ボスを希望するメンバー一覧を返します。
        早い者順になっています。
        /予約 /凸予約 /予定 でも反応します。
        """
        embed = discord.Embed(title='**現在の凸希望者**',color=0x0000ff)
        embed.add_field(name=f'{BOSSES[0]}',
        value='まだ誰もいません' if not self.res_b1 else '\n'.join(self.res_b1.values()),inline=False)
        embed.add_field(name=f'{BOSSES[1]}',
        value='まだ誰もいません' if not self.res_b2 else '\n'.join(self.res_b2.values()),inline=False)
        embed.add_field(name=f'{BOSSES[2]}',
        value='まだ誰もいません' if not self.res_b3 else '\n'.join(self.res_b3.values()),inline=False)
        embed.add_field(name=f'{BOSSES[3]}',
        value='まだ誰もいません' if not self.res_b4 else '\n'.join(self.res_b4.values()),inline=False)
        embed.add_field(name=f'{BOSSES[4]}',
        value='まだ誰もいません' if not self.res_b5 else '\n'.join(self.res_b5.values()),inline=False)
        await ctx.send(embed=embed)

    @commands.command(name=BOSSES[0],aliases=['b1','boss1'])
    async def res1(self, ctx, note=''):
        if self.overlap_check(ctx.author.id):
            await ctx.send('予約はひとり1つまでです。')
            return
        self.res_b1[ctx.author.id] = ctx.author.display_name\
            if not note else ctx.author.display_name + f': {note}'

    @commands.command(name=BOSSES[1],aliases=['b2','boss2'])
    async def res2(self, ctx, note=''):
        if self.overlap_check(ctx.author.id):
            await ctx.send('予約はひとり1つまでです。')
            return
        self.res_b2[ctx.author.id] = ctx.author.display_name\
            if not note else ctx.author.display_name + f': {note}'

    @commands.command(name=BOSSES[2],aliases=['b3','boss3'])
    async def res3(self, ctx, note=''):
        if self.overlap_check(ctx.author.id):
            await ctx.send('予約はひとり1つまでです。')
            return
        self.res_b3[ctx.author.id] = ctx.author.display_name\
            if not note else ctx.author.display_name + f': {note}'

    @commands.command(name=BOSSES[3],aliases=['b4','boss4'])
    async def res4(self, ctx, note=''):
        if self.overlap_check(ctx.author.id):
            await ctx.send('予約はひとり1つまでです。')
            return
        self.res_b4[ctx.author.id] = ctx.author.display_name\
            if not note else ctx.author.display_name + f': {note}'

    @commands.command(name=BOSSES[4],aliases=['b5','boss5'])
    async def res5(self, ctx, note=''):
        if self.overlap_check(ctx.author.id):
            await ctx.send('予約はひとり1つまでです。')
            return
        self.res_b5[ctx.author.id] = ctx.author.display_name\
            if not note else ctx.author.display_name + f': {note}'

    @commands.command(aliases=['凸完了','完了','クリア'])
    async def clear(self, ctx):  #予約を削除
        """
        実行したユーザーの凸希望を削除します。
        /凸完了 /完了 /クリア でも反応します。
        """
        if ctx.author.id in self.res_b1.keys():
            del self.res_b1[ctx.author.id]
        if ctx.author.id in self.res_b2.keys():
            del self.res_b2[ctx.author.id]
        if ctx.author.id in self.res_b3.keys():
            del self.res_b3[ctx.author.id]
        if ctx.author.id in self.res_b4.keys():
            del self.res_b4[ctx.author.id]
        if ctx.author.id in self.res_b5.keys():
            del self.res_b5[ctx.author.id]
# Bot本体側からコグを読み込む際に呼び出される関数。
def setup(bot):
    bot.add_cog(Reserve(bot))  # クラスにBotを渡してインスタンス化し、Botにコグとして登録する。
