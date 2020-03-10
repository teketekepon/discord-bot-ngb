# -*- coding: utf-8 -*-
import pyocr
import pyocr.builders
import pickle
from PIL import Image
import numpy as np
import aiohttp
import os
import re
import discord
from discord.ext import commands
from openpyxl import load_workbook

path_tesseract = r'./vendor/tesseract-ocr'
temp_path = r'./tmp/'
image_path = r'./downloads/image.png'
excel_path = r'./clan_battle_template.xlsx'
work_channel_id = 641248473546489876  # バトルログのスクショを貼るチャンネルのID
BOSSES = ['ワイバーン', 'ワイルドグリフォン', 'ライデン', 'ネプテリオン', 'アクアリオス']  # 1月のボス
STUMPS = ['〇', '△', '◆', '□', '◎', '☆']  # 左から[凸,1ボスLA,2ボスLA,3ボスLA,4ボスLA,5ボスLA]

class SaveResult(commands.Cog):
        # クラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
    def __init__(self, bot):
        self.bot = bot
        if not os.path.isfile(temp_path + 'col.pkl'):
            self.col = [3] * 30
            self.rej = 9
            pickle.dump(self.col, open(temp_path + 'col.pkl','wb'))
            pickle.dump(self.rej, open(temp_path + 'rej.pkl','wb'))
        else:
            self.col = pickle.load(open(temp_path + 'col.pkl','rb'))
            self.rej = pickle.load(open(temp_path + 'rej.pkl','rb'))

    def cog_unload(self):
        pickle.dump(self.col, open(temp_path + 'col.pkl','wb'))
        pickle.dump(self.rej, open(temp_path + 'rej.pkl','wb'))

    async def download_img(self, url, file_name):
        chunk_size = 32
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                if r.status == 200:
                    with open(file_name, mode = 'wb') as fi:
                        while True:
                            chunk = await r.content.read(chunk_size)
                            if not chunk:
                                break
                            fi.write(chunk)
        return

    def image_binarize(self, image):
        thresh = 193
        maxval = 255
        img_wigth = 1920
        img_height = 1080
        # アス比16:9なら読み取れる たぶん
        im = Image.open(image)
        # PIL.Imageからバトルログを切りだし
        im_hd = im.resize((img_wigth, img_height), Image.LANCZOS)
        im_crop = im_hd.crop(((img_wigth // 100) * 73,(img_height // 100) * 19,\
                            (img_wigth // 180) * 171,(img_height // 100) * 91))
        # numpyで2値化
        im_gray = np.array(im_crop.convert('L'))
        im_bin = (im_gray > thresh) * maxval
        # Save Binarized Image
        Image.fromarray(np.uint8(im_bin)).save(temp_path + 'temp.png')
        return

    def useOCR(self, image):
        # tesseractのpathを通す
        #if path_tesseract not in os.environ["PATH"].split(os.pathsep):
        #    os.environ["PATH"] += os.pathsep + path_tesseract
        #    os.environ["TESSDATA_PREFIX"] = path_tesseract + r'\tessdata'
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
        # log/ocr_result.txtにocr結果を保存
        print(text)
        with open('./log/ocr_result.txt', mode = 'w',encoding = 'UTF-8') as f:
            f.write(text)
        return text

    def save_excel(self, text):
        def get_value_list(t_2d):
            return([[cell.value for cell in tmp] for tmp in t_2d])

        attack = re.compile(r'[グジで\\](.+?)が(.+?)に(.\d+)')
        damege = re.compile(r'ダメージ.')
        # Excelファイルのロード(読み取り専用)
        workbook = load_workbook(excel_path)
        sheet = workbook['Battle_log']
        member_2l = get_value_list(sheet['A2:A31'])
        member = sum(member_2l, [])  # 2次元配列なので1次元化
        data = re.findall(attack, text)  # 名前とボスとダメージのリスト
        if len(data) < 4:
            print('一部うまく読み取れなかったようです')
        # 凸かLAか判定するためのリスト('ダメージ'or'ダメージで'で判定するため'で'で始まる名前の人がいると使えません)
        isLA = re.findall(damege, text)
        # こっから判定
        for n, m in enumerate(data):  # nは添え字,mはタプル
            isMatch = False
            for i, j in enumerate(member):  # iは添え字,jはリスト
                if j is None:
                    break
                name_match = re.search(j, m[0])
                if name_match is None:
                    continue
                else:
                    isMatch = True
                row = i + 2  # cell[A2]から始まるため+2する
                if self.col[i] == self.rej:
                    print('1日6個以上のスタンプは押せません')
                    return
                if 'で' in isLA[n]:
                    # LAなのでどのボスか判定
                    for x, y in enumerate(BOSSES):
                        boss_match = re.search(y, m[1])
                        if boss_match is not None:
                            stu = x + 1
                            break
                else:
                    # 凸なので〇スタンプをセット
                    stu = 0
                if  isMatch:
                    cell = sheet.cell(row = row, column = self.col[i], value = STUMPS[stu])
                    self.col[i] += 1
                continue
            if isMatch:
                print(f'{data[n]} は {cell} に\'{STUMPS[stu]}\'と書き込みました')
            else:
                print(f'{data[n]} はうまく読み取れませんでした')
        # Excelファイルのセーブ
        workbook.save(excel_path)
        # ロードしたExcelファイルを閉じる
        workbook.close()
        return

    @commands.group()
    async def day(self, ctx):
        if ctx.channel.id == work_channel_id:
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
                else:
                    mes = '現在6日目です'
                await ctx.send(f'{mes} サブコマンドで何日目か教えてください')

    @day.command('1')
    async def day1(self, ctx):
        self.col = [3] * 30
        self.rej = 9
        await ctx.send('記録位置を1日目にセットしました')

    @day.command('2')
    async def day2(self, ctx):
        self.col = [10] * 30
        self.rej = 16
        await ctx.send('記録位置を2日目にセットしました')

    @day.command('3')
    async def day3(self, ctx):
        self.col = [17] * 30
        self.rej = 23
        await ctx.send('記録位置を3日目にセットしました')

    @day.command('4')
    async def day4(self, ctx):
        self.col = [24] * 30
        self.rej = 30
        await ctx.send('記録位置を4日目にセットしました')

    @day.command('5')
    async def day5(self, ctx):
        self.col = [31] * 30
        self.rej = 37
        await ctx.send('記録位置を5日目にセットしました')

    @day.command('6')
    async def day6(self, ctx):
        self.col = [38] * 30
        self.rej = 44
        await ctx.send('記録位置を6日目にセットしました')

    @commands.command()
    async def pull(self, ctx):
        await ctx.send(file=discord.File(excel_path))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id == work_channel_id:
            if len(message.attachments) > 0:
                # messageに添付画像があり、特定のチャンネルの場合動作する
                await self.download_img(message.attachments[0].url, image_path)
                self.image_binarize(image_path)
                ocr_result = self.useOCR(temp_path + 'temp.png')
                if ocr_result is not None:
                    self.save_excel(ocr_result)
                # await message.channel.send(file=discord.File(temp_path + 'temp.png'))
# Bot本体側からコグを読み込む際に呼び出される関数。
def setup(bot):
    bot.add_cog(SaveResult(bot)) # クラスにBotを渡してインスタンス化し、Botにコグとして登録する。
