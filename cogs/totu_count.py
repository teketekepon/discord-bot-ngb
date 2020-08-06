# -*- coding: utf-8 -*-
import re
import pickle
import pyocr
import pyocr.builders
import aiohttp
import aiofiles
import discord
from PIL import Image
from .dbox import TransferData
from discord.ext import commands

TEMP_PATH = r'./tmp/'
IMAGE_PATH = r'./tmp/image0.png'

RESOLUTIONS = [(1280, 720),  # 1
                        (1334, 750),   # 2
                        (1920, 1080),  # 3 ここまで16:9
                        (2048, 1536),  # 4 4:3
                        (2224, 1668),  # 5 4:3 iPad
                        (2732, 2048),  # 6 4:3
                        (2880, 1440),  # 7 2_1 android
                        (3040, 1440),  # 8 2_1 Galaxy系(左160黒い)
                        (1792, 828),   # 9 19.5:9 iPhoneXR,11
                        (2436, 1125),  # 10 19.5:9 iPhoneX,XS,11Pro
                        (2688, 1242)]  # 11 19.5:9 iPhoneXS,11Pro max
# 作業チャンネルかを判定するcheck関数
def is_channel():
    def predicate(ctx):
        return ctx.channel.id in self.work_channel_id
    return commands.check(predicate)

class TotuCount(commands.Cog):
    """
    事前に登録したチャンネルにクラバトログのスクショを張ることで、凸の消化回数をカウントします。
    トリミングされている等の理由で規定の解像度から外れるとエラーになります。
    成功するとカウント数をメッセージするので確認してください。
    """
    # クラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
    def __init__(self, bot):
        self.bot = bot
        if TransferData().download_file(r'/totu.pkl', TEMP_PATH + 'totu.pkl'):
            with open(TEMP_PATH + 'totu.pkl','rb') as f:
                self.totu = pickle.load(f)
        else:
            self.totu = 0
        if TransferData().download_file(r'/work_channel_id.pkl', TEMP_PATH + 'work_channel_id.pkl'):
            with open(TEMP_PATH + 'work_channel_id.pkl','rb') as f:
                self.work_channel_id = pickle.load(f)
        else:
            self.work_channel_id = []  # 機能を有効にするチャンネルのID

    def cog_unload(self):
        with open(TEMP_PATH + 'totu.pkl','wb') as f:
            pickle.dump(self.totu, f)
        with open(TEMP_PATH + 'work_channel_id.pkl','wb') as f:
            pickle.dump(self.work_channel_id, f)
        TransferData().upload_file(TEMP_PATH + 'totu.pkl', r'/totu.pkl')
        TransferData().upload_file(TEMP_PATH + 'work_channel_id.pkl', r'/work_channel_id.pkl')

    async def download_img(self, url, file_name):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(file_name, mode = 'wb')
                    await f.write(await resp.read())
                    await f.close()

    def image_ocr(self, image):
        # バトルログを抽出(RESOLUTIONSにある解像度なら読み取れる)
        im = Image.open(image)
        for num, i in enumerate(RESOLUTIONS):
            if im.height - 10 < i[1] < im.height + 10 and im.width - 10 < i[0] < im.width + 10:
                if num <= 2:  # 16:9
                    im_hd = im.resize((1920, 1080), Image.LANCZOS)
                    im_crop = im_hd.crop((1400, 205, 1720, 920))
                elif num <= 5:  # 4:3 iPad
                    im_hd = im.resize((2224, 1668), Image.LANCZOS)
                    im_crop = im.crop((1625, 645, 1980, 1480))
                elif num == 6:  # 2_1 android
                    im_crop = im.crop((2200, 280, 2620, 1220))
                elif num == 7:  # 2_1 Galaxy
                    im_crop = im.crop((2360, 280, 2780, 1220))
                else:  # 19.5:9 iPhone
                    im_hd = im.resize((2668, 1242), Image.LANCZOS)
                    im_crop = im_hd.crop((1965, 225, 2290, 1000))
                break
        else:
            print('非対応の解像度です')
            return None
        # Pillowで2値化
        im_gray = im_crop.convert('L')
        im_bin = im_gray.point(lambda x: 255 if x > 193 else 0, mode='L')
        # 日本語と英数字をOCR
        tools = pyocr.get_available_tools()
        if len(tools) == 0:
            print('OCRtoolが読み込めません')
            return None
        tool = tools[0]
        res = tool.image_to_string(im_bin, lang='jpn',
        builder=pyocr.builders.WordBoxBuilder(tesseract_layout=6))
        text = ''
        for d in res:
            text = text + d.content
        return text

    def count(self, text):
        n = 0
        data = re.findall(r'ダメージで|ダメージ', text)  # OCRtextから凸判定材料のみ抽出
        # 'で'で始まるユーザーがいる場合そのひとつ前の凸がカウントされない場合がある
        if len(data) >= 5:
            del data[0]  # 1枚4件までのため
        for i in data:
            if not 'で' in i:
                n += 1
        return n

    @commands.command()
    async def reset(self, ctx):
        """
        凸カウントをリセットするコマンドです。
        """
        if ctx.channel.id in self.work_channel_id:
            self.totu = 0
            await ctx.send('凸カウントをリセットしました')

    @commands.command(aliases=['zanntotu','残凸','残り'])
    async def totu(self, ctx):
        """
        残凸数を返すコマンドです。
        """
        await ctx.send(f'現在 {self.totu} 凸消化して残り凸数は {90-self.totu} です')

    @commands.command()
    async def add(self, ctx, arg1):
        """
        凸カウントを増やすコマンドです。
        例えば /add 1 とすると1凸増やします。
        """
        if ctx.channel.id in self.work_channel_id:
            try:
                n = int(arg1)
            except ValueError:
                await ctx.send('引数が無効です')
                return
            self.totu += n
            await ctx.send(f'凸数を{n}足して{self.totu}になりました')

    @commands.command()
    async def sub(self, ctx, arg1):
        """
        凸カウントを減らすコマンドです。
        例えば /sub 1 とすると1凸減らします。
        """
        if ctx.channel.id in self.work_channel_id:
            try:
                n = int(arg1)
            except ValueError:
                await ctx.send('引数が無効です')
                return
            self.totu -= n
            await ctx.send(f'凸数を{n}引いて{self.totu}になりました')

    @commands.command()
    async def define(self, ctx):
        """
        機能を有効にするチャンネルとして登録するコマンドです。
        """
        if ctx.channel.id in self.work_channel_id:
            await ctx.send(f'{ctx.channel.name} はすでに作業チャンネルです')
        else:
            self.work_channel_id.append(ctx.channel.id)
            await ctx.send(f'{ctx.channel.name} を作業チャンネルに追加しました')

    @commands.command()
    async def remove(self, ctx):
        """
        機能を無効にするチャンネルとして登録するコマンドです。
        """
        if ctx.channel.id in self.work_channel_id:
            self.work_channel_id.remove(ctx.channel.id)
            await ctx.send(f'{ctx.channel.name} を作業チャンネルから除外しました')
        else:
            await ctx.send(f'{ctx.channel.name} は作業チャンネルではありません')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.channel.id in self.work_channel_id:
            if len(message.attachments) > 0:
                # messageに添付画像があり、指定のチャンネルの場合動作する
                await self.download_img(message.attachments[0].url, IMAGE_PATH)
                if (res := self.image_ocr(IMAGE_PATH)) is not None:
                    print(res,
                    end='\n--------------------OCR Result-------------------\n')
                    self.totu += self.count(res)
                else:
                    print('画像読み込みに失敗しました')
                # await message.channel.send(f'現在 {self.totu} 凸消化して残り凸数は {90-self.totu} です')
# Bot本体側からコグを読み込む際に呼び出される関数。
def setup(bot):
    bot.add_cog(TotuCount(bot)) # クラスにBotを渡してインスタンス化し、Botにコグとして登録する。
