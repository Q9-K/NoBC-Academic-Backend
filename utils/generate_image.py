from PIL import Image, ImageDraw, ImageFont
from utils.qos import upload_file,get_file
def generate_image(text):
    # 创建一个新的图片
    image = Image.new('RGB', (500, 500), color=(255,255,255))

    # 选择一个支持中文的字体和字体大小
    font_path = "simsun.ttc"  # 根据你的系统选择正确的字体路径
    font_size = 36
    font = ImageFont.truetype(font_path, font_size)

    # 初始化 ImageDraw
    draw = ImageDraw.Draw(image)

    # 要添加的文本


    # 试图使用 ImageDraw 对象的 textsize 方法
    try:
        text_width, text_height = draw.textsize(text, font=font)
    except AttributeError:
        # 如果 textsize 方法不存在，使用一个临时的方法来估计文本尺寸
        text_width, text_height = font.getmask(text).size

    # 计算文本的位置（居中）
    text_position = ((image.width - text_width) / 2, (image.height - text_height) / 2)

    # 将文本添加到图片上，设置文本颜色为白色
    draw.text(text_position, text, fill=(0, 0, 0), font=font)
    image.save(text+".png")

    if upload_file(text+".png",text+".png"):
        return get_file(text+".png")


if __name__ == '__main__':
    generate_image("北京航空航天大学")

