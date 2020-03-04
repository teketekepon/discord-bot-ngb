import pyocr
import pyocr.builders
from PIL import Image
import numpy as np
import aiohttp
import os
import re
import discord
from discord.ext import commands
from openpyxl import load_workbook

col = [3] * 30
work_channel_id = 641248473546489876  # バトルログのスクショを貼るチャンネルのID
BOSSES = ['ワイバーン', 'ワイルドグリフォン', 'ライデン', 'ネプテリオン', 'アクアリオス']  # 1月のボス
STUMPS = ['〇', '△', '◆', '□', '◎', '☆']  # 左から[凸,1ボスLA,2ボスLA,3ボスLA,4ボスLA,5ボスLA]

def image_binarize(image):
    thresh = 193
    maxval = 255
    img_wigth = 1280
    img_height = 720

    im = Image.open(image)
    # PIL.Imageからバトルログを切りだし
    im_hd = im.resize((img_wigth, img_height), Image.LANCZOS)
    im_crop = im_hd.crop(((img_wigth // 100) * 77,(img_height // 100) * 18,\
                        (img_wigth // 100) * 97,(img_height // 100) * 88))
    # numpyで2値化
    im_gray = np.array(im_crop.convert('L'))
    im_bin = (im_gray > thresh) * maxval
    # Save Cropped Image
    # im_crop.save('./tmp.png')
    # Save Binarized Image
    Image.fromarray(np.uint8(im_bin)).save('./tmp/tmp.png')
    return

async def download_img(url, file_name):
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

def useOCR(image):
    # tesseractのpathを通す
    path_tesseract = './tesseract'
    if path_tesseract not in os.environ['PATH'].split(os.pathsep):
        os.environ['PATH'] += os.pathsep + path_tesseract
        os.environ['TRSSDATA_PREFIX'] = path_tesseract + '/tessdata'
    tools = pyocr.get_available_tools()
    if len(tools) == 0:
        print('No OCR tool found')
        return
    tool = tools[0]
    # 日本語と英数字をOCR
    res = tool.image_to_string(Image.open(image),
                               lang='jpn+equ',
                               builder=pyocr.builders.WordBoxBuilder(tesseract_layout=6))
    text = ''
    for d in res:
        text = text + d.content
    # log/ocr_result.txtにocr結果を保存
    print(text)
    with open('./log/ocr_result.txt', mode = 'w',encoding = 'UTF-8') as f:
        f.write(text)
    return

def get_value_list(t_2d):
    return([[cell.value for cell in tmp] for tmp in t_2d])

def save_excel(text):
    with open(text, mode = 'r', encoding = 'UTF-8') as file:
        t = file.read()
    attack = re.compile(r'[グジで](.+?)が(.+?)に(\d+)ダメ')
    damege = re.compile(r'ダメージ.')
    # Excelファイルのロード(読み取り専用)
    excel_path = './clan_battle_template.xlsx'
    workbook = load_workbook(excel_path)
    sheet = workbook['Battle_log']
    member_2l = get_value_list(sheet['A2:A31'])
    member = sum(member_2l, [])  # 2次元配列なので1次元化
    data = re.findall(attack, t)  # 名前とボスとダメージのリスト
    if data is None:
        print('解析失敗')
    # 凸かLAか判定するためのリスト('ダメージ'or'ダメージで'で判定するため'で'で始まる名前の人がいると使えません)
    isLA = re.findall(damege, t)
    # こっから判定
    for n, m in enumerate(data):  # nは添え字,mはタプル
        isMatch = False
        for i, j in enumerate(member):  # iは添え字,jはリスト
            if member[i] is None:
                break
            name_match = re.search(member[i], m[0])
            if name_match is None:
                continue
            else:
                isMatch = True
            r = i + 2  # cell[A2]から始まるため+2する
            if 'で' in isLA[n]:
                # LAなのでどのボスか判定
                for x in range(len(BOSSES)):
                    boss_match = re.search(BOSSES[x], m[1])
                    if boss_match is not None:
                        stu = x + 1
                        isMatch = True
                        break
                if  isMatch:
                    cell = sheet.cell(row = r, column = col[i], value = STUMPS[stu])
                    col[i] += 1
                continue
            if isMatch:
                stu = 0
                cell = sheet.cell(row = r, column = col[i], value = STUMPS[stu])
                col[i] += 1
        if isMatch:
            print(f'{data[n]} は {cell} に\'{STUMPS[stu]}\'と書き込みました')
        else:
            print(f'{data[n]} はうまく読み取れなかった...')
    # Excelファイルのセーブ
    workbook.save(excel_path)
    # ロードしたExcelファイルを閉じる
    workbook.close()
    return

class SaveResult(commands.Cog):
        # クラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
    def __init__(self, bot):
        self.bot = bot
    # コグがアンロードされたとき・・
    def cog_unload(self):
        # ClientSessionを閉じます。
        # こうしないと「Unclosed client session」がでます
        self.session.close()

    @commands.group()
    async def day(self, ctx):
        if ctx.channel.id == work_channel_id:
            if ctx.invoked_subcommand is None:
                await ctx.send('サブコマンドが必要です。')

    @day.command('1')
    async def day1(self, ctx):
        for i in range(len(col)):
            col[i] = 3
        await ctx.send('記録位置を1日目にセットしました')

    @day.command('2')
    async def day2(self, ctx):
        for i in range(len(col)):
            col[i] = 10
        await ctx.send('記録位置を2日目にセットしました')

    @day.command('3')
    async def day3(self, ctx):
        for i in range(len(col)):
            col[i] = 17
        await ctx.send('記録位置を3日目にセットしました')

    @day.command('4')
    async def day4(self, ctx):
        for i in range(len(col)):
            col[i] = 24
        await ctx.send('記録位置を4日目にセットしました')

    @day.command('5')
    async def day5(self, ctx):
        for i in range(len(col)):
            col[i] = 31
        await ctx.send('記録位置を5日目にセットしました')

    @day.command('6')
    async def day6(self, ctx):
        for i in range(len(col)):
            col[i] = 38
        await ctx.send('記録位置を6日目にセットしました')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id == work_channel_id:
            if len(message.attachments) > 0:
                # messageに添付画像があり、特定のチャンネルの場合動作する
                await download_img(message.attachments[0].url, './downloads/image.png')
                image_binarize('./downloads/image.png')
                useOCR('./tmp/tmp.png')
                save_excel('./log/ocr_result.txt')
                await message.channel.send(file = discord.File('./tmp/tmp.png'))

# Bot本体側からコグを読み込む際に呼び出される関数。
def setup(bot):
    bot.add_cog(SaveResult(bot)) # クラスにBotを渡してインスタンス化し、Botにコグとして登録する。
