# -*- coding: utf-8 -*-

from io import BytesIO
import pickle
import re

import discord
from discord.ext import commands
from PIL import Image
import pyocr
import pyocr.builders

from .dbox import TransferData

TEMP_PATH = r'./tmp/'

class TotuCount(commands.Cog):
    """
    登録したチャンネルにクラバトログのスクショを張ることで、凸の消化回数をカウントします。
    チャンネルごとに個別にカウントされることに注意してください。
    トリミングされている等の理由で規定の解像度から外れるとエラーになります。
    """

    def __init__(self, bot):
        self.bot = bot
        # {key = channel.id value = count}
        self.totu = {}
        if TransferData().download_file(r'/totu.pkl',
        TEMP_PATH + 'totu.pkl'):
            with open(TEMP_PATH + 'totu.pkl','rb') as f:
                self.totu = pickle.load(f)

    def cog_unload(self):
        with open(TEMP_PATH + 'totu.pkl','wb') as f:
            pickle.dump(self.totu, f)
        TransferData().upload_file(TEMP_PATH + 'totu.pkl',
        r'/totu.pkl')

    def image_ocr(self, image):
        # バトルログを抽出(RESOLUTIONSにある解像度なら読み取れる)
        RESOLUTIONS = [
            (1280, 760),   # 0 DMM windows枠あり
            (1123, 628),   # 1
            (1280, 720),   # 2 DMM windows枠なし
            (1334, 750),   # 3 iPhone 7,8
            (1920, 1080),  # 4 ここまで16:9
            (2048, 1536),  # 5 4:3 iPad 9.7 mini
            (2224, 1668),  # 6 iPad Pro 10.5inch
            (2732, 2048),  # 7 iPad Pro 12.9inch
            (2388, 1668),  # 8 iPad Pro 11inch
            (2880, 1440),  # 9 2:1 android
            (3040, 1440),  # 10 2:1 Galaxy系(左160黒い)
            (1792, 828),   # 11 19.5:9 iPhoneXR,11
            (2436, 1125),  # 12 19.5:9 iPhoneX,XS,11Pro
            (2688, 1242)   # 13 19.5:9 iPhoneXS,11Pro max
        ]
        im = Image.open(image)
        for num, i in enumerate(RESOLUTIONS):
            # 解像度ごとに切り取り(+-10ピクセルは許容)
            if (im.height - 10 < i[1] < im.height + 10 and im.width
                    - 10 < i[0] < im.width + 10):
                if num == 0:
                    im_hd = im.resize((1920, 1080), Image.LANCZOS)
                    im_crop = im_hd.crop((1400, 245, 1720, 900))
                elif num <= 4:  # 16:9
                    im_hd = im.resize((1920, 1080), Image.LANCZOS)
                    im_crop = im_hd.crop((1400, 205, 1720, 920))
                elif num <= 7:  # 4:3 iPad1
                    im_hd = im.resize((2224, 1668), Image.LANCZOS)
                    im_crop = im.crop((1625, 645, 1980, 1480))
                elif num == 8:  # iPad2
                    im_crop = im.crop((1730, 545, 2140, 1430))
                elif num == 9:  # 2_1 android
                    im_crop = im.crop((2200, 280, 2620, 1220))
                elif num == 10:  # 2_1 Galaxy
                    im_crop = im.crop((2360, 280, 2780, 1220))
                else:  # 19.5:9 iPhone
                    im_hd = im.resize((2668, 1242), Image.LANCZOS)
                    im_crop = im_hd.crop((1965, 225, 2290, 1000))
                break
        else:
            print(f'{im.width}x{im.height}: 非対応の解像度です')
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
        builder = pyocr.builders.WordBoxBuilder(tesseract_layout=6)
        res = tool.image_to_string(im_bin, lang='jpn', builder=builder)
        text = ''
        for d in res:
            text = text + d.content
        return text

    def count(self, text):
        n = 0
        data = re.findall(r'ダメージで|ダメージ', text)
        # OCRtextから凸判定材料のみ抽出
        if len(data) >= 5:
            del data[0]  # スクショ1枚につき4件までのため
        for i in data:
            if not 'で' in i:
                n += 1
        return n

    @commands.command()
    async def reset(self, ctx):
        """
        凸カウントをリセットするコマンドです。
        """
        if ctx.channel.id in self.totu.keys():
            self.totu[ctx.channel.id] = 0
            await ctx.send('凸カウントをリセットしました')

    @commands.command(aliases=['zanntotu','残凸','残り'])
    async def totu(self, ctx):
        """
        残凸数をチャットするコマンドです。
        /zanntotu /残凸 /残り でも反応します。
        """
        if ctx.channel.id in self.totu.keys():
            await ctx.send(f'現在 {self.totu[ctx.channel.id]} 凸消化して'
                f'残り凸数は {90-self.totu[ctx.channel.id]} です')

    @commands.command()
    async def add(self, ctx, arg1):
        """
        凸カウントを増やすコマンドです。
        例えば /add 1 とすると1凸増やします。
        """
        if ctx.channel.id in self.totu.keys():
            try:
                n = int(arg1)
            except ValueError:
                await ctx.send('引数が無効です')
                return
            self.totu[ctx.channel.id] = self.totu[ctx.channel.id] + n
            await ctx.send(f'凸数を{n}足して{self.totu[ctx.channel.id]}になりました')

    @commands.command()
    async def sub(self, ctx, arg1):
        """
        凸カウントを減らすコマンドです。
        例えば /sub 1 とすると1凸減らします。
        """
        if ctx.channel.id in self.totu.keys():
            try:
                n = int(arg1)
            except ValueError:
                await ctx.send('引数が無効です')
                return
            self.totu[ctx.channel.id] = self.totu[ctx.channel.id] - n
            await ctx.send(f'凸数を{n}引いて{self.totu[ctx.channel.id]}になりました')

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def register(self, ctx):
        """
        機能を有効にするチャンネルとして登録するコマンドです。
        このコマンドは、manage_channels(チャンネルを編集)できるユーザーのみが使えます。
        """
        if ctx.channel.id in self.totu.keys():
            await ctx.send(f'{ctx.channel.name} はすでに凸カウントチャンネルです')
        else:
            self.totu[ctx.channel.id] = 0
            await ctx.send(f'{ctx.channel.name} を凸カウントチャンネルに追加しました')

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unregister(self, ctx):
        """
        機能を無効にするチャンネルとして登録するコマンドです。
        このコマンドは、manage_channels(チャンネルを編集)できるユーザーのみが使えます。
        """
        if ctx.channel.id in self.totu.keys():
            del self.totu[ctx.channel.id]
            await ctx.send(f'{ctx.channel.name} を凸カウントチャンネルから除外しました')
        else:
            await ctx.send(f'{ctx.channel.name} は凸カウントチャンネルではありません')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if not message.attachments:
            return

        if message.channel.id in self.totu.keys():
            # messageに添付画像があり、指定のチャンネルの場合動作する
            image = BytesIO(await message.attachments[0].read())
            if (res := self.image_ocr(image)) is not None:
                self.totu[message.channel.id] \
                    = self.totu[message.channel.id] + self.count(res)
                print(f'{message.channel.name} count: '\
                      f'{self.totu[message.channel.id]}')
            else:
                print('画像読み取りに失敗しました')

# Bot本体側からコグを読み込む際に呼び出される関数。
def setup(bot):
    bot.add_cog(TotuCount(bot)) # クラスにBotを渡してインスタンス化し、Botにコグとして登録する。
