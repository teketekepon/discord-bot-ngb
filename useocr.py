import pyocr
import pyocr.builders
import cv2
from PIL import Image
import os
import sys

# tesseractのpathを通す
path_tesseract = "./tesseract"
if path_tesseract not in os.environ["PATH"].split(os.pathsep):
    os.environ["PATH"] += os.pathsep + path_tesseract
    os.environ["TRSSDATA_PREFIX"] = path_tesseract + "/tessdata"

tools = pyocr.get_available_tools()

if len(tools) == 0:
    print("No OCR tool found")
    sys.exit(1)

tool = tools[0]

# 日本語と英数字をOCR
res = tool.image_to_string(Image.open("./tmp/tmp.png"),
                           lang="jpn",
                           builder=pyocr.builders.WordBoxBuilder(tesseract_layout=6))

out = cv2.imread("./tmp/tmp.png")
text = ""
for d in res:
    text = text + d.content
    print(d.content)
    print(d.position)
    cv2.rectangle(out, d.position[0], d.position[1], (0, 0, 255), 2)
# log/ocr_result.txtにocr結果を保存
with open("./log/ocr_result.txt", mode = "w") as f:
    f.write(text)
# DEBUG プレビュー
cv2.imshow("img",out)
cv2.waitKey(0)
cv2.destroyAllWindows()
