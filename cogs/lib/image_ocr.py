import logging

from PIL import Image
import pyocr


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


class ImageOcr:

    def __init__(self):
        self.logger = logging.getLogger('discord.ImageOcr')

    def image_ocr(self, image):
        im = Image.open(image)
        for num, i in enumerate(RESOLUTIONS):
            # 解像度ごとに切り取り(+-10ピクセルは許容)
            if (im.height - 13 < i[1] < im.height + 13
                    and im.width - 10 < i[0] < im.width + 10):
                if num == 0:
                    im = im.crop((930, 210, 1155, 640))
                elif num <= 6:  # 16:9
                    im = im.crop((int(im.width*0.73), int(im.height*0.239),
                                  int(im.width*0.895), int(im.height*0.847)))
                elif num <= 9:  # 4:3 iPad1
                    im = im.crop((int(im.width*0.73), int(im.height*0.43),
                                  int(im.width*0.9), int(im.height*0.885)))
                elif num == 10:  # iPad2
                    im = im.crop((1760, 630, 2160, 1425))
                elif num == 11:  # 2_1 android
                    im = im.crop((int(im.width*0.76), int(im.height*0.243),
                                  int(im.width*0.91), int(im.height*0.842)))
                elif num <= 13:  # 2_1 Galaxy
                    im = im.crop((int(im.width*0.773), int(im.height*0.241),
                                  int(im.width*0.917), int(im.height*0.838)))
                else:  # 19.5:9 iPhone
                    im = im.crop((int(im.width*0.733), int(im.height*0.227),
                                  int(im.width*0.866), int(im.height*0.79)))
                break
        else:
            self.logger.error('%d x %d: 非対応の解像度です', im.width, im.height)
            return None
        # Pillowで2値化
        im = im.convert('L')
        im_bin = im.point(lambda x: 255 if x > 193 else 0, mode='L')
        # 日本語と英数字をOCR
        tools = pyocr.get_available_tools()
        if len(tools) == 0:
            self.logger.error('OCRtoolが読み込めません')
            return None
        tool = tools[0]
        builder = pyocr.builders.WordBoxBuilder(tesseract_layout=6)
        res = tool.image_to_string(im_bin, lang='jpn', builder=builder)
        text = ''
        for d in res:
            text = text + d.content
        return text
