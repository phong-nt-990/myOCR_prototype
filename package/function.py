import io
from PIL import Image
from PyQt6.QtGui import QImage
from PyQt6.QtCore import QBuffer


def toPILImage(object: QImage):
    img = object
    buffer = QBuffer()
    img.save(buffer, "PNG")
    pil_im = Image.open(io.BytesIO(buffer.data()))
    return pil_im


def removeLineBreak(input : str):
    res = input.replace("\n", " ")
    return res