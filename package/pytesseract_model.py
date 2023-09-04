from PIL import Image
import pytesseract


class Model:
    def __init__(self, image: Image, choice: str):
        self.text = None
        self.image_original = image
        self.choice = choice

    def picToString(self):
        if self.choice == "1":
            res = pytesseract.image_to_string(self.image_original, lang="vie")
        else:
            res = pytesseract.image_to_string(self.image_original, lang="eng")
        return res
