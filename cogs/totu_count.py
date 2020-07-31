# -*- coding: utf-8 -*-
import os
import re
import pickle
import pyocr
import pyocr.builders
import numpy as np
import aiohttp
import aiofiles
import discord
from PIL import Image
from discord.ext import commands

TEMP_PATH = r'./tmp/'
IMAGE_PATH = r'./downloads/image0.png'

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

class TotuCount(commands.Cog):
    # クラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
    def __init__(self, bot):
        self.bot = bot
        if not os.path.isfile(TEMP_PATH + 'totu.pkl'):
            self.totu = 0
            self.work_channel_id = []  # 機能を有効にするチャンネルのID
        else:
            self.totu = pickle.load(open(TEMP_PATH + 'totu.pkl','rb'))
            self.work_channel_id = pickle.load(open(TEMP_PATH + 'work_channel_id.pkl','rb'))

    def cog_unload(self):
        pickle.dump(self.totu, open(TEMP_PATH + 'totu.pkl','wb'))
        pickle.dump(self.work_channel_id, open(TEMP_PATH + 'work_channel_id.pkl','wb'))

    async def download_img(self, url, file_name):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(file_name, mode = 'wb')
                    await f.write(await resp.read())
                    await f.close()

    # スクショからバトルログを抽出し2値化する関数
    def image_binarize(self, image):
        # RESOLUTIONSにある解像度なら読み取れる
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
            return False
        # numpyで2値化
        im_gray = np.array(im_crop.convert('L'))
        im_bin = (im_gray > 193) * 255
        if np.count_nonzero(im_bin == 0) > im_bin.size // 10 * 9:
            return False
        # Save Binarized Image
        Image.fromarray(np.uint8(im_bin)).save(TEMP_PATH + 'temp.png')
        return True

    def use_ocr(self, image):
        # ローカル環境の場合tesseractのpathを通す heroku環境の場合buildpackを使用するため不要
        # if path_tesseract not in os.environ["PATH"].split(os.pathsep):
        #     os.environ["PATH"] += os.pathsep + r'./vendor/tesseract-ocr'
        #     os.environ["TESSDATA_PREFIX"] = r'./vendor/tesseract-ocr/share/tessdata'
        tools = pyocr.get_available_tools()
        if len(tools) == 0:
            print('No OCR tool found')
            return
        tool = tools[0]
        # 日本語と英数字をOCR
        res = tool.image_to_string(Image.open(image),
                                   lang='jpn',  # 'jpn+eng'
                                   builder=pyocr.builders.WordBoxBuilder(tesseract_layout=6))
        text = ''
        for d in res:
            text = text + d.content
        print(text, end='\n--------------------OCR Result-------------------\n')
        return text

    def count(self, text):
        n = 0
        data = re.findall(r'ダメージで|ダメージ', text)  # OCRtextから凸判定材料のみ抽出
        # 'で'で始まるユーザーがいる場合そのひとつ前の凸がカウントされない場合がある
        if len(data) >= 5:
            del data[0]  # 1枚4件までのため
        for i in data:
            if not 'で' in i:
                self.totu += 1
                n += 1
        return n

    @commands.command()  # 凸カウントをリセットするコマンド
    async def clear(self, ctx):
        if ctx.channel.id in self.work_channel_id:
            self.totu = 0
            await ctx.send('凸カウントをリセットしました')
        else:
            await ctx.send('このチャンネルでの操作は許可されていません')

    @commands.command()  # 残凸数を返すコマンド
    async def totu(self, ctx):
        await ctx.send(f'現在 {self.totu} 凸して残り凸数は {90-self.totu} です')

    @commands.command()  # 凸カウントを増やすコマンド
    async def add(self, ctx, arg1):
        try:
            n = int(arg1)
        except ValueError:
            await ctx.send('引数が無効です')
            return
        self.totu += n
        await ctx.send(f'凸数を{n}足して{self.totu}になりました')

    @commands.command()  # 凸カウントを増やすコマンド
    async def sub(self, ctx, arg1):
        try:
            n = int(arg1)
        except ValueError:
            await ctx.send('引数が無効です')
            return
        self.totu -= n
        await ctx.send(f'凸数を{n}引いて{self.totu}になりました')

    @commands.command()  # 機能を有効にするチャンネルとして登録するコマンド
    async def define(self, ctx):
        if ctx.channel.id in self.work_channel_id:
            await ctx.send(f'{ctx.channel.name} はすでに作業チャンネルです')
        else:
            self.work_channel_id.append(ctx.channel.id)
            await ctx.send(f'{ctx.channel.name} を作業チャンネルに追加しました')

    @commands.command()  # 機能を無効にするチャンネルとして登録するコマンド
    async def remove(self, ctx):
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
                if self.image_binarize(IMAGE_PATH):
                    ocr_result = self.use_ocr(TEMP_PATH + 'temp.png')
                    if ocr_result is not None:
                        x = self.count(ocr_result)
                        await ctx.send(f'{n}凸カウント')
                    else:
                        await ctx.send('画像読み込みに失敗しました')
# Bot本体側からコグを読み込む際に呼び出される関数。
def setup(bot):
    bot.add_cog(TotuCount(bot)) # クラスにBotを渡してインスタンス化し、Botにコグとして登録する。