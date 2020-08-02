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
    各メンバー1つずつ凸を希望するボスを/ボス名 コマンドで登録します。
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
        if user in res_b1 or user in res_b2 or user in res_b3 or user in res_b4 or user in res_b5:
            return True
        return False

    @commands.command(aliases=['予約','凸予約','予定'])
    async def yoyaku(self, ctx):  # 予約内容の確認
        """
        各ボスを希望するメンバー一覧を返します。
        早い者順になっています。
        /予約 /凸予約 /予定 でも反応します。
        """
        content = ''
        embed = discord.Embed(title='現在の凸希望者', description=content, color=0x0000ff)
        content += f'`{BOSSES[0]}`\n```'
        content += '\n'.join(res_b1) + '```\n'
        content += f'`{BOSSES[1]}`\n```'
        content += '\n'.join(res_b2) + '```\n'
        content += f'`{BOSSES[2]}`\n```'
        content += '\n'.join(res_b3) + '```\n'
        content += f'`{BOSSES[3]}`\n```'
        content += '\n'.join(res_b4) + '```\n'
        content += f'`{BOSSES[4]}`\n```'
        content += '\n'.join(res_b5) + '```'
        await ctx.send(embed=embed)

    @commands.command(name=BOSSES[0])
    async def res1(self, ctx, note):
        if self.overlap_check(ctx.author.name):
            await ctx.send('予約はひとり1つまでです。')
            return
        res_b1.append(ctx.author.name)

    @commands.command(name=BOSSES[1])
    async def res2(self, ctx):
        if self.overlap_check(ctx.author.name):
            await ctx.send('予約はひとり1つまでです。')
            return
        res_b2.append(ctx.author.name)

    @commands.command(name=BOSSES[2])
    async def res3(self, ctx):
        if self.overlap_check(ctx.author.name):
            await ctx.send('予約はひとり1つまでです。')
            return
        res_b3.append(ctx.author.name)

    @commands.command(name=BOSSES[3])
    async def res4(self, ctx):
        if self.overlap_check(ctx.author.name):
            await ctx.send('予約はひとり1つまでです。')
            return
        res_b4.append(ctx.author.name)

    @commands.command(name=BOSSES[4])
    async def res5(self, ctx):
        if self.overlap_check(ctx.author.name):
            await ctx.send('予約はひとり1つまでです。')
            return
        res_b5.append(ctx.author.name)

    @commands.command(aliases=['凸完了','完了','クリア'])
    async def kantotu(self, ctx):  #予約を削除
        """
        実行したユーザーの凸希望を削除します。
        /凸完了 /完了 /クリア でも反応します。
        """
        if ctx.author.name in res_b1:
            res_b1.remove(ctx.author.name)
        if ctx.author.name in res_b2:
            res_b2.remove(ctx.author.name)
        if ctx.author.name in res_b3:
            res_b3.remove(ctx.author.name)
        if ctx.author.name in res_b4:
            res_b4.remove(ctx.author.name)
        if ctx.author.name in res_b5:
            res_b5.remove(ctx.author.name)
# Bot本体側からコグを読み込む際に呼び出される関数。
def setup(bot):
    bot.add_cog(Reserve(bot))  # クラスにBotを渡してインスタンス化し、Botにコグとして登録する。
