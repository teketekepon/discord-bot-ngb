from PIL import Image
import numpy as np
import os
import sys
import aiohttp
import asyncio
import discord
from discord.ext import commands
work_channel_id = 641248473546489876

def image_binarize(image):
    thresh = 193
    maxval = 255
    img_wigth = 1280
    img_height = 720

    im = Image.open(image)

    # PIL.Imageからバトルログを切りだし
    im_hd = im.resize((img_wigth, img_height), Image.LANCZOS)
    im_crop = im_hd.crop(((img_wigth // 100) * 77,(img_height // 100) * 18,\
                        (img_wigth // 100) * 97,(img_height // 100) * 88))

    # numpyで2値化
    im_gray = np.array(im_crop.convert('L'))
    im_bin = (im_gray > thresh) * maxval

    # Save Cropped Image
    #im_crop.save('./tmp.png')

    # Save Binarized Image
    Image.fromarray(np.uint8(im_bin)).save('./tmp/tmp.png')

async def download_img(url, file_name):
    chunk_size = 32
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            if r.status == 200:
                with open("./tmp/" + file_name, mode = 'wb') as f:
                    while True:
                        chunk = await r.content.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)

# コグとして用いるクラスを定義。
class Ngb(commands.Cog):

    # TestCogクラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
    def __init__(self, bot):
        self.bot = bot

    # コマンドの作成。コマンドはcommandデコレータで必ず修飾する。
    @commands.command()
    async def ping(self, ctx):
        await ctx.send('pong!')

    @commands.group()
    async def role(self, ctx):
        # サブコマンドが指定されていない場合、メッセージを送信する。
        if ctx.invoked_subcommand is None:
            await ctx.send('サブコマンド(操作,人,役職)が必要です。')

    @role.command()
    async def add(self, ctx, member: discord.Member, role: discord.Role):
        await member.add_roles(role)

    @role.command()
    async def remove(self, ctx, member: discord.Member, role: discord.Role):
        await member.remove_roles(role)

    @commands.command()
    async def bot(self,ctx):
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
            await channel.send(f'{ctx.author.mention} タイムアウト')
        else:
            #すでにいずれかの権限がある場合削除
            find = discord.utils.find(lambda o: o.name == '王宮', msg.guild.roles)
            if find is not None:
                await msg.author.remove_roles(find)
            find = discord.utils.find(lambda o: o.name == '宮殿', msg.guild.roles)
            if find is not None:
                await msg.author.remove_roles(find)
            find = discord.utils.find(lambda o: o.name == '城下町', msg.guild.roles)
            if find is not None:
                await msg.author.remove_roles(find)
            #対応する権限を付与
            if msg.content == '1':
                role = discord.utils.get(msg.guild.roles, name = '王宮')
                await msg.author.add_roles(role)
                reply = f'{msg.author.mention} をロール「王宮」へ割り振ったわ 感謝しなさい！'
                await msg.channel.send(reply)
            elif msg.content == '2':
                role = discord.utils.get(msg.guild.roles, name = '宮殿')
                await msg.author.add_roles(role)
                reply = f'{msg.author.mention} をロール「宮殿」へ割り振ったわ 感謝しなさい！'
                await msg.channel.send(reply)
            elif msg.content == '3':
                role = discord.utils.get(msg.guild.roles, name = '城下町')
                await msg.author.add_roles(role)
                reply = f'{msg.author.mention} をロール「城下町」へ割り振ったわ 感謝しなさい！'
                await msg.channel.send(reply)


    @commands.Cog.listener()
    async def on_member_join(self, member):
        dm = member.dm_channel
        if dm is None:
            dm = await member.create_dm()
        await dm.send(f'{member.mention} さん。ナイトガーデングループへようこそ！'\
                      '\n温泉郷チャンネルで「/bot」と発言すると、あなたの所属するクラン'\
                      '専用のチャットが見れるようになります。ご活用ください！')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id == work_channel_id:
            if len(message.attachments) > 0:
                # messageに添付画像があり、特定のチャンネルの場合動作する
                await download_img(message.attachments[0].url, "image.png")
                image_binarize("./tmp/image.png")
                await message.channel.send(file = discord.File("./tmp/tmp.png"))
            return

# Bot本体側からコグを読み込む際に呼び出される関数。
def setup(bot):
    bot.add_cog(Ngb(bot)) # TestCogにBotを渡してインスタンス化し、Botにコグとして登録する。
