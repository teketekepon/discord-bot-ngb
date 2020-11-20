# -*- coding: utf-8 -*-

import logging
from io import BytesIO
import pickle
import re
import time
import threading

from discord.ext import commands

from cogs.lib.dbox import TransferData
from cogs.lib.image_ocr import ImageOcr

TEMP_PATH = r'./tmp/'


class TotuCount(commands.Cog):
    """
    バトルログのスクショから凸の消化回数をカウントします。
    チャンネルごとに個別にカウントされることに注意してください。
    トリミングされている等の理由で規定の解像度から外れるとエラーになります。
    """

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord.TotuCount')
        # {key = channel.id value = count}
        self.totu = {}
        self.rev = TransferData().download_file(r'/totu.pkl',
                                                TEMP_PATH + 'totu.pkl')
        if self.rev is not None:
            with open(TEMP_PATH + 'totu.pkl', 'rb') as f:
                self.totu = pickle.load(f)
            self.logger.info('Pickle loaded')
        th = threading.Thread(target=self.second_download)
        th.setDaemon(True)
        th.start()

    def second_download(self):
        time.sleep(120)
        tmp = TransferData().download_file(r'/totu.pkl', TEMP_PATH+'totu.pkl')
        if self.rev is not None and tmp is not None and self.rev != tmp:
            with open(TEMP_PATH + 'totu.pkl', 'rb') as f:
                self.totu = pickle.load(f)
                self.logger.info('Second Pickle loaded')

    def cog_unload(self):
        """シャットダウン時に変数をDropboxへ保存"""
        with open(TEMP_PATH + 'totu.pkl', 'wb') as f:
            pickle.dump(self.totu, f)
        TransferData().upload_file(TEMP_PATH + 'totu.pkl', r'/totu.pkl')
        self.logger.info('Pickle saved')

    def count(self, text):
        """テキストから凸数をカウント"""
        n = 0
        data = re.findall(r'ダメージで|ダメージ', text)
        # OCRtextから凸判定材料のみ抽出
        if len(data) >= 5:
            del data[0]  # スクショ1枚につき4件までのため
        for i in data:
            if 'で' not in i:
                n += 1
        return n

    @commands.command()
    async def reset(self, ctx):
        """
        凸カウントをリセットするコマンド
        """
        if ctx.channel.id in self.totu.keys():
            self.totu[ctx.channel.id] = 0
            await ctx.send('凸カウントをリセットしました')

    @commands.command(aliases=['zanntotu', '残凸', '残り'])
    async def totu(self, ctx):
        """
        残凸数をチャットするコマンド
        `/zanntotu` `/残凸` `/残り` でも反応します。
        """
        if ctx.channel.id in self.totu.keys():
            await ctx.send(f'現在 {self.totu[ctx.channel.id]} 凸消化して'
                           f'残り凸数は {90-self.totu[ctx.channel.id]} です')

    @commands.command()
    async def add(self, ctx, arg: int):
        """
        凸カウントを増やすコマンド
        例えば `/add 1` とすると1凸増やします。
        """
        if ctx.channel.id in self.totu.keys():
            self.totu[ctx.channel.id] = self.totu[ctx.channel.id] + arg
            await ctx.send(f'凸数を{arg}足して{self.totu[ctx.channel.id]}になりました')

    @commands.command()
    async def sub(self, ctx, arg: int):
        """
        凸カウントを減らすコマンド
        例えば `/sub 1` とすると1凸減らします。
        """
        if ctx.channel.id in self.totu.keys():
            self.totu[ctx.channel.id] = self.totu[ctx.channel.id] - arg
            await ctx.send(f'凸数を{arg}引いて{self.totu[ctx.channel.id]}になりました')

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def register(self, ctx):
        """
        機能を有効にするチャンネルとして登録するコマンド
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
        機能を無効にするチャンネルとして登録するコマンド
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
                res = ImageOcr().image_ocr(image)
                if res is not None:
                    a = self.count(res)
                    self.totu[message.channel.id] += a
                    # await message.channel.send(f'{a}凸カウント')
                    self.logger.info('%s count: %d', message.channel.name, a)
                else:
                    # await ctx.send('画像読み取りに失敗しました')
                    self.logger.error('画像読み取りに失敗しました')


# Bot本体側からコグを読み込む際に呼び出される関数。
def setup(bot):
    bot.add_cog(TotuCount(bot))  # クラスにBotを渡してインスタンス化し、Botにコグとして登録する。
