# -*- coding: utf-8 -*-
import os
import re
import pickle
import typing
import pyocr
import pyocr.builders
import numpy as np
import aiohttp
import aiofiles
import discord
from PIL import Image
from openpyxl import load_workbook
from discord.ext import commands

TEMP_PATH = r'./tmp/'
IMAGE_PATH = r'./downloads/image.png'
EXCEL_PATH = r'./BattleLog.xlsx'
BOSSES = ['ワイバーン', 'グリフォン', 'マダムプリズム', 'サイクロプス', 'メサルティム']  # 3月のボス
STUMPS = ['△', '◆', '□', '◎', '☆', '〇', '?']  # 左から[1ボスLA,2ボスLA,3ボスLA,4ボスLA,5ボスLA,凸,不明]
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

class SaveResult(commands.Cog):
    # クラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
    def __init__(self, bot):
        self.bot = bot
        if not os.path.isfile(TEMP_PATH + 'col.pkl'):
            self.col = [3] * 30
            self.rej = 9
            self.totu = 0
            self.work_channel_id = []  # バトルログのスクショを貼るチャンネルのID
        else:
            self.col = pickle.load(open(TEMP_PATH + 'col.pkl','rb'))
            self.rej = pickle.load(open(TEMP_PATH + 'rej.pkl','rb'))
            self.totu = pickle.load(open(TEMP_PATH + 'totu.pkl','rb'))
            self.work_channel_id = pickle.load(open(TEMP_PATH + 'work_channel_id.pkl','rb'))

    def cog_unload(self):
        pickle.dump(self.col, open(TEMP_PATH + 'col.pkl','wb'))
        pickle.dump(self.rej, open(TEMP_PATH + 'rej.pkl','wb'))
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
                                   lang='jpn+eng',
                                   builder=pyocr.builders.WordBoxBuilder(tesseract_layout=6))
        text = ''
        for d in res:
            text = text + d.content
        print(text, end='\n--------------------OCR Result-------------------\n')
        return text

    def member_edit(self, op=None, *member):
        wb = load_workbook(EXCEL_PATH)
        sheet = wb['Battle_log']
        mlist = sum([[cell.value for cell in tmp] for tmp in sheet['A2:A31']], [])
        temp = []
        if op is None:
            wb.close()
            return ','.join(map(str, mlist))
        elif op == 'add':
            for m in member:
                if mlist not in member:
                    for i, item in enumerate(mlist):
                        if item is None:
                            mlist[i] = m
                            break
                temp.append(m)
        elif op == 'remove':
            for m in member:
                try:
                    mlist.remove(m)
                    mlist.append('')
                except ValueError:
                    temp.append(m)
        elif op == 'delete':
            if all(mlist):
                for i, item in enumerate(mlist):
                    if item is None:
                        mlist[i-1] = ''
                        break
            else:
                mlist[30] = ''
        elif op == 'clear':
            mlist = ['' for n in range(30)]
        else:
            wb.close()
            return ','.join(map(str, mlist))
        mlist = sorted(mlist, key=lambda x: (x is None, x))
        for num, w in enumerate(mlist):
            sheet.cell(row=num+2, column=1, value=w)
        wb.save(EXCEL_PATH)
        wb.close()
        return ','.join(map(str, mlist))

    def save_excel(self, text):
        wb = load_workbook(EXCEL_PATH)
        sheet = wb['Battle_log']
        member = sum([[cell.value for cell in tmp] for tmp in sheet['A2:A31']], [])  # excelからメンバーリストを取得
        text = re.sub(r'[A-MP-Z]+?[\u2012-\u2015][A-MP-Z]*?', 'ダメージで', text)  # 誤認識が多いため置換
        print(text, end='\n-----------------------置換後----------------------\n')
        data = re.findall(r'[グジで\S](.+?)が(.+?)に(.[\doO]+)(?=([ダ].{4}))', text)  # 名前とボスとダメージのリスト抽出
        # 凸かLAか判定するためのリスト('ダメージ'or'ダメージで'で判定するため'で'で始まる名前の人がいると誤認します)
        for n, m in enumerate(reversed(data)):  # nは添え字,mはタプル
            isMatch = False
            for i, j in enumerate(member):  # iは添え字,jはリスト
                if j is None:  # 空のセルは判定しない
                    break
                name_match = re.search(re.escape(j), m[0])
                if name_match is None:
                    continue
                else:
                    isMatch = True
                row = i + 2  # cell[A2]から始まるため+2する
                if self.col[i] == self.rej:
                    print(f'{m} 1日6個以上のスタンプは押せません')
                    return
                if 'で' in m[3]:
                    for x, y in enumerate(BOSSES):  # LAなのでどのボスか判定
                        boss_match = re.search(y, m[1])
                        if boss_match is not None:
                            stu = x
                            break
                else:
                    stu = 5  # 凸なので〇スタンプをセット
                if  isMatch:
                    cell = sheet.cell(row=row, column=self.col[i], value=STUMPS[stu])
                    self.col[i] += 1
                    if stu == 5:
                        self.totu += 1
                continue
            if isMatch:
                print(f'{m} は\'{cell.coordinate}\'に\'{STUMPS[stu]}\'と書き込みました')
            else:
                print(f'{m} はメンバーとマッチしなかった為書き込まれません')
        # Excelファイルをセーブして閉じる
        wb.save(EXCEL_PATH)
        wb.close()

    # clearコマンドで利用する関数
    def clear_excel(self, kwd):
        # 任意のセルを始点に2次元配列を書き込む関数
        def write_list_2d(sheet, l_2d, start_row, start_col):
            for y, row in enumerate(l_2d):
                for x, cell in enumerate(row):
                    sheet.cell(row=start_row + y, column=start_col + x, value=l_2d[y][x])
        # 6*30の空の2次元配列を作る
        blank_list = [['' for row in range(6)] for col in range(30)]
        wb = load_workbook(EXCEL_PATH)
        sheet = wb['Battle_log']
        if kwd == 'day1':  # 内容をクリア
            write_list_2d(sheet, blank_list, 2, 3)
        elif kwd == 'day2':
            write_list_2d(sheet, blank_list, 2, 10)
        elif kwd == 'day3':
            write_list_2d(sheet, blank_list, 2, 17)
        elif kwd == 'day4':
            write_list_2d(sheet, blank_list, 2, 24)
        elif kwd == 'day5':
            write_list_2d(sheet, blank_list, 2, 31)
        elif kwd == 'day6':
            write_list_2d(sheet, blank_list, 2, 38)
        elif kwd == 'all':
            for i in range(3, 39, 7):
                write_list_2d(sheet, blank_list, 2, i)
        else:
            print('clear_excel error: 無効な引数です')
            return False
        # Excelファイルをセーブして閉じる
        wb.save(EXCEL_PATH)
        wb.close()
        return True

    @commands.command()  # 記録する位置を変更するコマンド 全員の列位置が変更される
    async def day(self, ctx, a :typing.Optional[int] = None):
        if ctx.channel.id in self.work_channel_id:
            if a is not None:
                if 0 < a < 6:
                    self.col = [3+7*(a-1)] * 30
                    self.rej = 9+7*(a-1)
                    self.totu = 0
                    await ctx.send(f'記録位置を{a}日目にセットしました')
                else:
                    await ctx.send('引数は半角数字の1～6で入力してください')
            else:
                if self.rej == 9:
                    mes = '現在1日目です'
                elif self.rej == 16:
                    mes = '現在2日目です'
                elif self.rej == 23:
                    mes = '現在3日目です'
                elif self.rej == 30:
                    mes = '現在4日目です'
                elif self.rej == 37:
                    mes = '現在5日目です'
                elif self.rej == 44:
                    mes = '現在6日目です'
                await ctx.send(f'{mes} 引数で何日目か教えてください 1～6')
        else:
            await ctx.send('このチャンネルでの操作は許可されていません\n'
                                      '/append コマンドで作業チャンネルに登録してください')

    @commands.command()  # セルの内容を消去(Noneに上書き)するコマンド
    async def clear(self, ctx, a: typing.Optional[str] = None):
        if ctx.channel.id in self.work_channel_id:
            if a is not None:
                if len(a) < 2:
                    b = self.clear_excel('day' + a)
                else:
                    b = self.clear_excel(a)
                if b:
                    self.col = [self.rej - 6] * 30
                    self.totu = 0
                    await ctx.send(f'「{a}」日目の内容を消去しました\nそれに伴い記録位置もリセットされました')
                else:
                    await ctx.send('引数が無効です')
            else:
                await ctx.send('何日目の記録を消去するか指定してください(1～6 または all)')
        else:
            await ctx.send('このチャンネルでの操作は許可されていません\n'
                                      '/append コマンドで作業チャンネルに登録してください')

    @commands.command()
    async def member(self, ctx, op=None, *member):
        if ctx.channel.id in self.work_channel_id:
            res = self.member_edit(op, *member)
            await ctx.send(f'現在のメンバー一覧です\n{res}')
        else:
            await ctx.send('このチャンネルでの操作は許可されていません\n'
                                      '/append コマンドで作業チャンネルに登録してください')

    @commands.command()
    async def pull(self, ctx):
        if ctx.channel.id in self.work_channel_id:
            await ctx.send(file=discord.File(EXCEL_PATH))

    @commands.command()
    async def totu(self, ctx):
        await ctx.send(f'残り凸数は {90-self.totu} です')

    @commands.command()
    async def append(self, ctx):
        if ctx.channel.id in self.work_channel_id:
            await ctx.send(f'{ctx.channel.name} はすでに作業チャンネルです')
        else:
            self.work_channel_id.append(ctx.channel.id)
            await ctx.send(f'{ctx.channel.name} を作業チャンネルに追加しました')

    @commands.command()
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
                        self.save_excel(ocr_result)
# Bot本体側からコグを読み込む際に呼び出される関数。
def setup(bot):
    bot.add_cog(SaveResult(bot)) # クラスにBotを渡してインスタンス化し、Botにコグとして登録する。
