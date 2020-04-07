# -*- coding: utf-8 -*-
import pyocr
import pyocr.builders
import pickle
import numpy as np
import aiohttp
import aiofiles
import os
import re
import discord
from PIL import Image
from openpyxl import load_workbook
from discord.ext import commands

temp_path = r'./tmp/'
image_path = r'./downloads/image.png'
excel_path = r'./BattleLog.xlsx'
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
        if not os.path.isfile(temp_path + 'col.pkl'):
            self.col = [3] * 30
            self.rej = 9
            self.totu = 0
            self.work_channel_id = []  # バトルログのスクショを貼るチャンネルのID
        else:
            self.col = pickle.load(open(temp_path + 'col.pkl','rb'))
            self.rej = pickle.load(open(temp_path + 'rej.pkl','rb'))
            self.totu = pickle.load(open(temp_path + 'totu.pkl','rb'))
            self.work_channel_id = pickle.load(open(temp_path + 'work_channel_id.pkl','rb'))

    def cog_unload(self):
        pickle.dump(self.col, open(temp_path + 'col.pkl','wb'))
        pickle.dump(self.rej, open(temp_path + 'rej.pkl','wb'))
        pickle.dump(self.totu, open(temp_path + 'totu.pkl','wb'))
        pickle.dump(self.work_channel_id, open(temp_path + 'work_channel_id.pkl','wb'))

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
        Image.fromarray(np.uint8(im_bin)).save(temp_path + 'temp.png')
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

    def save_excel(self, text):
        wb = load_workbook(excel_path)
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
        wb.save(excel_path)
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
        wb = load_workbook(excel_path)
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
        # Excelファイルをセーブして閉じる
        wb.save(excel_path)
        wb.close()

    @commands.group()  # 記録する位置を変更するコマンドグループ 全員の列位置が変更される
    async def day(self, ctx):
        if ctx.channel.id in self.work_channel_id:
            if ctx.invoked_subcommand is None:
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
                else:
                    return
                await ctx.send(f'{mes} サブコマンドで何日目か教えてください ([1-6])')

    @day.command('1')
    async def day1(self, ctx):
        if ctx.channel.id in self.work_channel_id:
            self.col = [3] * 30
            self.rej = 9
            self.totu = 0
            await ctx.send('記録位置を1日目にセットしました')
    @day.command('2')
    async def day2(self, ctx):
        if ctx.channel.id in self.work_channel_id:
            self.col = [10] * 30
            self.rej = 16
            self.totu = 0
            await ctx.send('記録位置を2日目にセットしました')
    @day.command('3')
    async def day3(self, ctx):
        if ctx.channel.id in self.work_channel_id:
            self.col = [17] * 30
            self.rej = 23
            self.totu = 0
            await ctx.send('記録位置を3日目にセットしました')
    @day.command('4')
    async def day4(self, ctx):
        if ctx.channel.id in self.work_channel_id:
            self.col = [24] * 30
            self.rej = 30
            self.totu = 0
            await ctx.send('記録位置を4日目にセットしました')
    @day.command('5')
    async def day5(self, ctx):
        if ctx.channel.id in self.work_channel_id:
            self.col = [31] * 30
            self.rej = 37
            self.totu = 0
            await ctx.send('記録位置を5日目にセットしました')
    @day.command('6')
    async def day6(self, ctx):
        if ctx.channel.id in self.work_channel_id:
            self.col = [38] * 30
            self.rej = 44
            self.totu = 0
            await ctx.send('記録位置を6日目にセットしました')

    @commands.group()  # セルの内容を消去(Noneに上書き)するコマンドグループ
    async def clear(self, ctx):
        if ctx.channel.id in self.work_channel_id:
            if ctx.invoked_subcommand is None:
                await ctx.send('サブコマンドで何日目の記録を消去するか指定してください([1-6] または all)')

    @clear.command('1')
    async def clear_day1(self, ctx):
        if ctx.channel.id in self.work_channel_id:
            self.clear_excel('day1')
            await ctx.send('1日目の記録内容を消去しました')
    @clear.command('2')
    async def clear_day2(self, ctx):
        if ctx.channel.id in self.work_channel_id:
            self.clear_excel('day2')
            await ctx.send('2日目の記録内容を消去しました')
    @clear.command('3')
    async def clear_day3(self, ctx):
        if ctx.channel.id in self.work_channel_id:
            self.clear_excel('day3')
            await ctx.send('3日目の記録内容を消去しました')
    @clear.command('4')
    async def clear_day4(self, ctx):
        if ctx.channel.id in self.work_channel_id:
            self.clear_excel('day4')
            await ctx.send('4日目の記録内容を消去しました')
    @clear.command('5')
    async def clear_day5(self, ctx):
        if ctx.channel.id in self.work_channel_id:
            self.clear_excel('day5')
            await ctx.send('5日目の記録内容を消去しました')
    @clear.command('6')
    async def clear_day6(self, ctx):
        if ctx.channel.id in self.work_channel_id:
            self.clear_excel('day6')
            await ctx.send('6日目の記録内容を消去しました')
    @clear.command('all')
    async def clear_all(self, ctx):
        if ctx.channel.id in self.work_channel_id:
            self.clear_excel('all')
            await ctx.send('すべての記録内容を消去しました')

    @commands.group()
    async def member(self, ctx):
        if ctx.channel.id in self.work_channel_id:
            if ctx.invoked_subcommand is None:
                await ctx.send(f'現在のメンバー一覧です\n')

    @member.command()
    async def add(self, ctx):
        if ctx.channel.id in self.work_channel_id:
            await ctx.send(f'{ctx.content}をメンバーに登録します')
            await ctx.send(f'現在のメンバー一覧です\n')

    @member.command()
    async def remove(self, ctx):
        if ctx.channel.id in self.work_channel_id:
            await ctx.send(f'{ctx.content}をメンバーにから削除します')
            await ctx.send(f'現在のメンバー一覧です\n')

    @commands.command()
    async def pull(self, ctx):
        if ctx.channel.id in self.work_channel_id:
            await ctx.send(file=discord.File(excel_path))

    @commands.command('残凸')
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
                await self.download_img(message.attachments[0].url, image_path)
                if self.image_binarize(image_path):
                    ocr_result = self.use_ocr(temp_path + 'temp.png')
                    if ocr_result is not None:
                        self.save_excel(ocr_result)
# Bot本体側からコグを読み込む際に呼び出される関数。
def setup(bot):
    bot.add_cog(SaveResult(bot)) # クラスにBotを渡してインスタンス化し、Botにコグとして登録する。
