# -*- coding: utf-8 -*-

import os
import discord
from discord.ext import commands
import traceback
import logging
# ロギングを定義
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='./log/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
# Botアカウントへのアクセストークン(herokuの環境変数にしまってある)
TOKEN = os.environ["ACCESS_TOKEN"]
# 読み込むコグの名前を格納しておく。
INITIAL_EXTENSIONS = [
    'cogs.ngb',
    'cogs.reserve',
    'cogs.totu_count',
]
# クラスの定義。ClientのサブクラスであるBotクラスを継承。
class MyBot(commands.Bot):
    # MyBotのコンストラクタ。
    def __init__(self, command_prefix):
        # スーパークラスのコンストラクタに値を渡して実行。
        super().__init__(command_prefix)
        # INITIAL_COGSに格納されている名前から、コグを読み込む。
        # エラーが発生した場合は、エラー内容を表示。
        for cog in INITIAL_EXTENSIONS:
            try:
                self.load_extension(cog)
            except Exception:
                traceback.print_exc()

    # Botの準備完了時に呼び出されるイベント
    async def on_ready(self):
        print('--------------')
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('--------------')


# MyBotのインスタンス化及び起動処理。
if __name__ == '__main__':
    bot = MyBot(command_prefix='/') # command_prefixはコマンドの最初の文字として使うもの。
    bot.run(TOKEN) # Botを動かす
