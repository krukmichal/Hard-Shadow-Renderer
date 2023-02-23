from PIL import Image
import sys
import os

path = os.path.abspath("") + "/"
processed = False

def processImage(path):
    with Image.open(path) as img:
        name = os.path.basename(path)
        height = img.height / 3
        width = img.width / 4
        file_extension = ".png"
        names = []
        names.append(f'images/{name}_top{file_extension}')
        img.crop((width, 0, 2 * width, height)).rotate(180).save(names[0])

        names.append(f'images/{name}_left{file_extension}')
        img.crop((0, width, width, 2 * height)).save(names[1])

        names.append(f'images/{name}_front{file_extension}')
        img.crop((width, height, 2 * width, 2 * height)).save(names[2])

        names.append(f'images/{name}_right{file_extension}')
        img.crop((2 * width, height, 3 * width, 2 * height)).save(names[3])

        names.append(f'images/{name}_back{file_extension}')
        img.crop((3 * width, height, 4 * width, 2 * height)).save(names[4])

        names.append(f'images/{name}_bottom{file_extension}')
        img.crop((width, 2 * height, 2 * width, 3 * height)).rotate(180).save(names[5])

        return names
