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

class MyBot(commands.Bot):
    def __init__(self, command_prefix, help_command):
        # スーパークラスのコンストラクタに値を渡して実行。
        super().__init__(command_prefix, help_command)
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

class Help(commands.HelpCommand):
    """Helpコマンドの定義"""

    def __init__(self):
        super().__init__()
        self.no_category = 'カテゴリ未設定'
        self.command_attrs['description'] = 'コマンドリストを表示します。'

    def command_not_found(self,string):  # コマンドが見つからない場合
        return f'{string} というコマンドは存在しません。'

    def subcommand_not_found(self,command,string):  # サブコマンドが見つからない場合
        if isinstance(command, commands.Group) and len(command.all_commands) > 0:
            return f'{command.qualified_name} に {string} というサブコマンドは登録されていません。'
        return f'{command.qualified_name} にサブコマンドは登録されていません。'

    async def send_bot_help(self,mapping):  # 引数なしのhelpコマンドの場合
        content = '機能、コマンド一覧\n'
        for cog in mapping:  # 各コグのコマンド一覧を content に追加していく
            command_list = await self.filter_commands(mapping[cog])
            if not command_list:  # 表示できるコマンドがないので、他のコグの処理に移る
                continue
            if cog is None:  # コグが未設定のコマンドなので、no_category属性を参照する
                content += f'```\n{self.no_category}```'
            else:
                content += f'\n**{cog.qualified_name}**\n```{cog.description}```\nコマンドリスト\n'
            for command in command_list:
                content += f'`{self.context.prefix}{command.name}` : {command.short_doc}\n'
        embed = discord.Embed(title=f'NGBヘルプ', description=content,color=0x00ff00)
        embed.set_footer(text=f'詳しいヘルプ {self.context.prefix}help 機能名またはコマンド名')
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self,cog):  # cogが指定された場合
        content = ''
        command_list = await self.filter_commands(cog.get_commands())
        content += f'```\n{cog.qualified_name} : {cog.description}```\n'
        for command in command_list:
            content += f'`{self.context.prefix}{command.name}` : {command.help}\n'
        content += '\n'
        if command_list[0] is None:
            content = '__表示できるコマンドがありません。__'
        embed = discord.Embed(title=f'{cog.qualified_name}',description=content,color=0x00ff00)
        embed.set_footer(text=f'コマンドのヘルプ {self.context.prefix}help コマンド名')
        await self.get_destination().send(embed=embed)

    async def send_command_help(self,command):  # commandが指定された場合
        embed = discord.Embed(title=self.get_command_signature(command),description=command.short_doc,color=0x00ff00)
        if command.help:
            embed.add_field(name="ヘルプテキスト：",value=command.help,inline=False)
        embed.set_footer(text=f"コマンドのヘルプ {self.context.prefix}help コマンド名")
        await self.get_destination().send(embed=embed)

    async def send_error_message(self,error):  # エラー発生時
        embed = discord.Embed(title='ヘルプ表示のエラー',description=error,
            color=0xff0000)
        await self.get_destination().send(embed=embed)

if __name__ == '__main__':
    # MyBotのインスタンス化及び起動処理。
    bot = MyBot(command_prefix='/', help_command=Help()) # command_prefixはコマンドの最初の文字として使うもの。
    bot.run(TOKEN) # Botを動かす
