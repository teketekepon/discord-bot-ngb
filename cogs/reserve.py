# -*- coding: utf-8 -*-
import pickle
import os
import discord
from discord.ext import commands
from itertools import zip_longest

TEMP_PATH = r'./tmp/'
BOSSES = ['ワイバーン', 'ランドスロース', 'ムシュフシュ', 'ティタノタートル', 'オルレオン']  # 7月のボス
res_b1 = []
res_b2 = []
res_b3 = []
res_b4 = []
res_b5 = []

class Reserve(commands.Cog):
    """
    ボスの凸希望をディスコード上で管理します。
    各メンバー1つずつ凸を希望するボスを/(ボス名) (備考)コマンドで登録します。
    例: /ワイバーン 物理ワンパン
    """
    # クラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
    def __init__(self, bot):
        self.bot = bot
        if os.path.isfile(TEMP_PATH + 'res.pkl'):
            self.res = pickle.load(open(TEMP_PATH + 'res.pkl','rb'))
            a, b, c, d, e = zip(*self.res)
            if (ax := sum(not None for i in a)) != 0:
                for i, x in enumerate(range(ax)):
                    res_b1.append(a[x])
            if (bx := sum(not None for i in b)) != 0:
                for i, x in enumerate(range(bx)):
                    res_b2.append(b[x])
            if (cx := sum(not None for i in c)) != 0:
                for i, x in enumerate(range(cx)):
                    res_b3.append(c[x])
            if (dx := sum(not None for i in d)) != 0:
                for i, x in enumerate(range(dx)):
                    res_b4.append(d[x])
            if (ex := sum(not None for i in e)) != 0:
                for i, x in enumerate(range(ex)):
                    res_b5.append(e[x])

    def cog_unload(self):
        self.res = zip_longest(res_b1, res_b2, res_b3, res_b4, res_b5)
        pickle.dump(self.res, open(TEMP_PATH + 'res.pkl','wb'))

    def overlap_check(self, user):  # 重複防止
        list = res_b1+res_b2+res_b3+res_b4+res_b5
        for i in list:
            if user in i:
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
        embed.add_field(name=f'{BOSSES[0]}',value='\u200' + ' '.join(res_b1))
        embed.add_field(name=f'{BOSSES[1]}',value='\u200' + ' '.join(res_b2))
        embed.add_field(name=f'{BOSSES[2]}',value='\u200' + ' '.join(res_b3))
        embed.add_field(name=f'{BOSSES[3]}',value='\u200' + ' '.join(res_b4))
        embed.add_field(name=f'{BOSSES[4]}',value='\u200' + ' '.join(res_b5))
        await ctx.send(embed=embed)

    @commands.command(name=BOSSES[0])
    async def res1(self, ctx, note=None):
        if self.overlap_check(ctx.author.display_name):
            await ctx.send('予約はひとり1つまでです。')
            return
        res_b1.append(ctx.author.display_name + ':' + note or '')

    @commands.command(name=BOSSES[1])
    async def res2(self, ctx, note=None):
        if self.overlap_check(ctx.author.display_name):
            await ctx.send('予約はひとり1つまでです。')
            return
        res_b2.append(ctx.author.display_name + ':' + note or '')

    @commands.command(name=BOSSES[2])
    async def res3(self, ctx, note=None):
        if self.overlap_check(ctx.author.display_name):
            await ctx.send('予約はひとり1つまでです。')
            return
        res_b3.append(ctx.author.display_name + ':' + note or '')

    @commands.command(name=BOSSES[3])
    async def res4(self, ctx, note=None):
        if self.overlap_check(ctx.author.display_name):
            await ctx.send('予約はひとり1つまでです。')
            return
        res_b4.append(ctx.author.display_name + ':' + note or '')

    @commands.command(name=BOSSES[4])
    async def res5(self, ctx, note=None):
        if self.overlap_check(ctx.author.display_name):
            await ctx.send('予約はひとり1つまでです。')
            return
        res_b5.append(ctx.author.display_name + ':' + note or '')

    @commands.command(aliases=['凸完了','完了','クリア'])
    async def kantotu(self, ctx):  #予約を削除
        """
        実行したユーザーの凸希望を削除します。
        /凸完了 /完了 /クリア でも反応します。
        """
        for i, str in enumerate(res_b1):
            if ctx.author.display_name in str:
                del res_b1[i]
        for i, str in enumerate(res_b2):
            if ctx.author.display_name in str:
                del res_b2[i]
        for i, str in enumerate(res_b3):
            if ctx.author.display_name in str:
                del res_b3[i]
        for i, str in enumerate(res_b4):
            if ctx.author.display_name in str:
                del res_b4[i]
        for i, str in enumerate(res_b5):
            if ctx.author.display_name in str:
                del res_b5[i]
# Bot本体側からコグを読み込む際に呼び出される関数。
def setup(bot):
    bot.add_cog(Reserve(bot))  # クラスにBotを渡してインスタンス化し、Botにコグとして登録する。
