`tesseract <img_path> <img_tesseract_result_name> -l chi_sim -psm 6 makebox`

-l <lang>
# 设置识别语言类型，支持多种语言混合识别(即lang用+链接)
另，查看支持语言可通过调用`tesseract --list-langs`
官方支持语言：https://github.com/tesseract-ocr/tessdata
新增支持语言：将*.traineddata拷贝至/usr/local/Cellar/tesseract/3.05.02/share/tessdata/

-psm
# 识别图像的方式
具体支持类型可使用`tesseract --help-psm`查看

makebox
# 输出坐标信息

