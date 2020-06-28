# -*- coding: utf-8 -*-
import pickle
import os
import discord
from discord.ext import commands
from itertools import zip_longest

TEMP_PATH = r'./tmp/'
BOSSES = ['ワイバーン', 'グリフォン', 'マダムプリズム', 'サイクロプス', 'メサルティム']  # 3月のボス
res_b1 = []
res_b2 = []
res_b3 = []
res_b4 = []
res_b5 = []

class Reserve(commands.Cog):
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

    @commands.command()
    async def yoyaku(self, ctx):
        boss1 = '|'.join(res_b1)
        boss2 = '|'.join(res_b2)
        boss3 = '|'.join(res_b3)
        boss4 = '|'.join(res_b4)
        boss5 = '|'.join(res_b5)
        await ctx.send(f'現在の予約状況\n{BOSSES[0]} | {boss1} |\n{BOSSES[1]} | {boss2} |\n'
        f'{BOSSES[2]} | {boss3} |\n{BOSSES[3]} | {boss4} |\n{BOSSES[4]} | {boss5}|')

    @commands.command(name=BOSSES[0])
    async def res1(self, ctx):
        if ctx.author.name in res_b1:
            return
        res_b1.append(ctx.author.name)

    @commands.command(name=BOSSES[1])
    async def res2(self, ctx):
        if ctx.author.name in res_b2:
            return
        res_b2.append(ctx.author.name)

    @commands.command(name=BOSSES[2])
    async def res3(self, ctx):
        if ctx.author.name in res_b3:
            return
        res_b3.append(ctx.author.name)

    @commands.command(name=BOSSES[3])
    async def res4(self, ctx):
        if ctx.author.name in res_b4:
            return
        res_b4.append(ctx.author.name)

    @commands.command(name=BOSSES[4])
    async def res5(self, ctx):
        if ctx.author.name in res_b5:
            return
        res_b5.append(ctx.author.name)

    @commands.command(name='凸完了')
    async def kantotu(self, ctx):
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
          #予約を削除
# Bot本体側からコグを読み込む際に呼び出される関数。
def setup(bot):
    bot.add_cog(Reserve(bot))  # クラスにBotを渡してインスタンス化し、Botにコグとして登録する。
