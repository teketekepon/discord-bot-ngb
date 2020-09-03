# -*- coding: utf-8 -*-

import logging
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
    凸の消化回数をカウントします。
    チャンネルごとに個別にカウントされることに注意してください。
    トリミングされている等の理由で規定の解像度から外れるとエラーになります。
    """

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord.TotuCount')
        # {key = channel.id value = count}
        self.totu = {}
        if TransferData().download_file(r'/totu.pkl', TEMP_PATH + 'totu.pkl'):
            with open(TEMP_PATH + 'totu.pkl', 'rb') as f:
                self.totu = pickle.load(f)
                self.logger.info('Pickle loaded')

    def cog_unload(self):
        with open(TEMP_PATH + 'totu.pkl', 'wb') as f:
            pickle.dump(self.totu, f)
        TransferData().upload_file(TEMP_PATH + 'totu.pkl', r'/totu.pkl')
        self.logger.info('Pickle saved')

    def image_ocr(self, image):
        """バトルログを抽出(RESOLUTIONSにある解像度なら読み取れる)"""
        RESOLUTIONS = [
            (1280, 760),   # 0 DMM windows枠あり
            (1000, 565),   # 1
            (1123, 628),   # 2
            (1280, 720),   # 3 DMM windows枠なし
            (1334, 750),   # 4 iPhone 7,8
            (1920, 1080),  # 5
            (2560, 1440),  # 6 ここまで16:9
            (2048, 1536),  # 7 4:3 iPad 9.7 mini
            (2224, 1668),  # 8 iPad Pro 10.5inch
            (2732, 2048),  # 9 iPad Pro 12.9inch
            (2388, 1668),  # 10 iPad Pro 11inch
            (2880, 1440),  # 11 2:1 android
            (2160, 1023),  # 12 2:1 Galaxy系
            (3040, 1440),  # 13 2:1 Galaxy系(左160黒い)
            (1792, 828),   # 14 19.5:9 iPhoneXR,11
            (2436, 1125),  # 15 19.5:9 iPhoneX,XS,11Pro
            (2688, 1242)   # 16 19.5:9 iPhoneXS,11Pro max
        ]
        im = Image.open(image)
        for num, i in enumerate(RESOLUTIONS):
            # 解像度ごとに切り取り(+-10ピクセルは許容)
            if (im.height - 13 < i[1] < im.height + 13
                    and im.width - 10 < i[0] < im.width + 10):
                if num == 0:
                    im_crop = im.crop((930, 210, 1155, 640))
                elif num <= 6:  # 16:9
                    im_crop = im.crop((int(im.width*0.73), int(im.height*0.239),
                                       int(im.width*0.895), int(im.height*0.847)))
                elif num <= 9:  # 4:3 iPad1
                    im_crop = im.crop((int(im.width*0.73), int(im.height*0.43),
                                       int(im.width*0.9), int(im.height*0.885)))
                elif num == 10:  # iPad2
                    im_crop = im.crop((1760, 630, 2160, 1425))
                elif num == 11:  # 2_1 android
                    im_crop = im.crop((int(im.width*0.76), int(im.height*0.243),
                                       int(im.width*0.91), int(im.height*0.842)))
                elif num <= 13:  # 2_1 Galaxy
                    im_crop = im.crop((int(im.width*0.773), int(im.height*0.241),
                                       int(im.width*0.917), int(im.height*0.838)))
                else:  # 19.5:9 iPhone
                    im_crop = im.crop((int(im.width*0.733), int(im.height*0.227),
                                       int(im.width*0.866), int(im.height*0.79)))
                break
        else:
            self.logger.error('%d x %d: 非対応の解像度です', im.width, im.height)
            return None
        # Pillowで2値化
        im_gray = im_crop.convert('L')
        im_bin = im_gray.point(lambda x: 255 if x > 193 else 0, mode='L')
        # 日本語と英数字をOCR
        tools = pyocr.get_available_tools()
        
        if len(tools) == 0:
            self.logger.error('OCRtoolが読み込めません')
            return None
        for tool in tools:
            print(tool.get_name())
        tool = tools[0]
        builder = pyocr.builders.WordBoxBuilder(tesseract_layout=6)
        res = tool.image_to_string(im_bin, lang='jpn', builder=builder)
        text = ''
        for d in res:
            text = text + d.content
        return text

    def count(self, text):
        """テキストから凸数をカウント"""
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

    @commands.command(aliases=['zanntotu', '残凸', '残り'])
    async def totu(self, ctx):
        """
        残凸数をチャットするコマンドです。
        `/zanntotu` `/残凸` `/残り` でも反応します。
        """
        if ctx.channel.id in self.totu.keys():
            await ctx.send(f'現在 {self.totu[ctx.channel.id]} 凸消化して'
                           f'残り凸数は {90-self.totu[ctx.channel.id]} です')

    @commands.command()
    async def add(self, ctx, arg: int):
        """
        凸カウントを増やすコマンドです。
        例えば `/add 1` とすると1凸増やします。
        """
        if ctx.channel.id in self.totu.keys():
            self.totu[ctx.channel.id] = self.totu[ctx.channel.id] + arg
            await ctx.send(f'凸数を{arg}足して{self.totu[ctx.channel.id]}になりました')

    @commands.command()
    async def sub(self, ctx, arg: int):
        """
        凸カウントを減らすコマンドです。
        例えば `/sub 1` とすると1凸減らします。
        """
        if ctx.channel.id in self.totu.keys():
            self.totu[ctx.channel.id] = self.totu[ctx.channel.id] - arg
            await ctx.send(f'凸数を{arg}引いて{self.totu[ctx.channel.id]}になりました')

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
            for i in message.attachments:
                image = BytesIO(await i.read())
                if (res := self.image_ocr(image)) is not None:
                    a = self.count(res)
                    self.totu[message.channel.id] += a
                    # await message.channel.send(f'{a}凸カウント')
                    self.logger.info('%s count: %d', message.channel.name, a)
                else:
                    # await ctx.send('画像読み取りに失敗しました')
                    self.logger.error('画像読み取りに失敗しました')

# Bot本体側からコグを読み込む際に呼び出される関数。
def setup(bot):
    bot.add_cog(TotuCount(bot)) # クラスにBotを渡してインスタンス化し、Botにコグとして登録する。
