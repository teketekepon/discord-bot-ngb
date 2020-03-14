# -*- coding: utf-8 -*-
import asyncio
import discord
from discord.ext import commands

class Ngb(commands.Cog):
    # クラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
    def __init__(self, bot):
        self.bot = bot

    # コマンドの作成。コマンドはcommandデコレータで必ず修飾する。
    @commands.group()
    async def role(self, ctx):
        # サブコマンドが指定されていない場合、メッセージを送信する。
        if ctx.invoked_subcommand is None:
            await ctx.send('サブコマンド(add or remove,member,role)が必要です。')

    @role.command()
    async def add(self, ctx, member: discord.Member, role: discord.Role):
        await member.add_roles(role)

    @role.command()
    async def remove(self, ctx, member: discord.Member, role: discord.Role):
        await member.remove_roles(role)

    @commands.command()
    async def bot(self, ctx):
        await ctx.send(f'{ctx.author.mention} 割り振り先を選びなさい♪(1:王宮2:宮殿3:城下町)')

        def check(n):
            if n.content.startswith('1'):
                return n.content == '1' and n.author == ctx.author
            if n.content.startswith('2'):
                return n.content == '2' and n.author == ctx.author
            if n.content.startswith('3'):
                return n.content == '3' and n.author == ctx.author

        try:
            msg = await self.bot.wait_for('message',timeout = 20.0,check = check)
        except asyncio.TimeoutError:
            await ctx.send(f'{ctx.author.mention} タイムアウト')
        else:
            # すでにいずれかのroleがある場合削除
            find = discord.utils.find(lambda o: o.name == '王宮', msg.guild.roles)
            if find is not None:
                await msg.author.remove_roles(find)
            find = discord.utils.find(lambda o: o.name == '宮殿', msg.guild.roles)
            if find is not None:
                await msg.author.remove_roles(find)
            find = discord.utils.find(lambda o: o.name == '城下町', msg.guild.roles)
            if find is not None:
                await msg.author.remove_roles(find)
            # 対応する権限を付与
            if msg.content == '1':
                role = discord.utils.get(msg.guild.roles, name = '王宮')
                await msg.author.add_roles(role)
                reply = f'{msg.author.mention} をロール「{role}」へ割り振ったわ 感謝しなさい！'
                await msg.channel.send(reply)
            elif msg.content == '2':
                role = discord.utils.get(msg.guild.roles, name = '宮殿')
                await msg.author.add_roles(role)
                reply = f'{msg.author.mention} をロール「{role}」へ割り振ったわ 感謝しなさい！'
                await msg.channel.send(reply)
            elif msg.content == '3':
                role = discord.utils.get(msg.guild.roles, name = '城下町')
                await msg.author.add_roles(role)
                reply = f'{msg.author.mention} をロール「{role}」へ割り振ったわ 感謝しなさい！'
                await msg.channel.send(reply)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        dm = member.dm_channel
        if dm is None:
            dm = await member.create_dm()
        await dm.send(f'{member.mention} さん。ナイトガーデングループへようこそ！'\
                                '\n温泉郷チャンネルで「/bot」と発言すると、あなたの所属するクラン'\
                                '専用のチャットが見れるようになります。ご活用ください！')

# Bot本体側からコグを読み込む際に呼び出される関数。
def setup(bot):
    bot.add_cog(Ngb(bot))  # クラスにBotを渡してインスタンス化し、Botにコグとして登録する。
