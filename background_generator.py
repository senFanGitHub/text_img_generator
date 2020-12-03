import cv2
import math
import os
import random
import numpy as np

from PIL import Image, ImageDraw, ImageFilter

def gaussian_noise(height, width):
    """
        Create a background with Gaussian noise (to mimic paper)
    """

    # We create an all white image
    mean = random.randint(100,255)
    image = np.ones((height, width)) * 100

    # We add gaussian noise
    cv2.randn(image,mean , 10)

    return Image.fromarray(image).convert('RGBA')

def plain_white(height, width):
    """
        Create a plain white background
    """

    return Image.new("L", (width, height), 255).convert('RGBA')

def quasicrystal(height, width):
    """
        Create a background with quasicrystal (https://en.wikipedia.org/wiki/Quasicrystal)
    """

    image = Image.new("L", (width, height))
    pixels = image.load()

    frequency = random.random() * 30 + 20 # frequency
    phase = random.random() * 2 * math.pi # phase
    rotation_count = random.randint(10, 20) # of rotations

    for kw in range(width):
        y = float(kw) / (width - 1) * 4 * math.pi - 2 * math.pi
        for kh in range(height):
            x = float(kh) / (height - 1) * 4 * math.pi - 2 * math.pi
            z = 0.0
            for i in range(rotation_count):
                r = math.hypot(x, y)
                a = math.atan2(y, x) + i * math.pi * 2.0 / rotation_count
                z += math.cos(r * math.sin(a) * frequency + phase)
            c = int(255 - round(255 * z / rotation_count))
            pixels[kw, kh] = c # grayscale
    return image.convert('RGBA')

def picture(height, width,font_color):
    """
        Create a background with a picture
    """

    # 查看字体颜色先
    r=int(font_color[1:3],16)
    g=int(font_color[3:5],16)
    b=int(font_color[5:7],16)
    text_c={r:'r',
    g:'g',
    b:'b'}
    
    max_f =min([r,g,b])
    text_color =text_c[max_f]

    pictures = os.listdir('./pictures')
    
    pic_index=0
    # 检验图片颜色
    while True:
#         pic_index = random.randint(0, len(pictures) - 1)
        img=cv2.imread('./pictures/' + pictures[1])
        
        roi=img[0:10,0:10].transpose(2,0,1)
        
        B=sum(sum(roi[0]))
        G=sum(sum(roi[1]))
        R=sum(sum(roi[2]))
        bg_c={R:'r',G:'g',B:'b'}
        max_b=min([R,G,B])
        bg_color=bg_c[max_b]
        
        if bg_color!=text_color:
            break
       
        
        
    if len(pictures) > 0:
        picture = Image.open('./pictures/' + pictures[pic_index])

        if picture.size[0] < width:
            picture = picture.resize([width, int(picture.size[1] * (width / picture.size[0]))], Image.ANTIALIAS)
        elif picture.size[1] < height:
            picture.thumbnail([int(picture.size[0] * (height / picture.size[1])), height], Image.ANTIALIAS)

        if (picture.size[0] == width):
            x = 0
        else:
            x = random.randint(0, picture.size[0] - width)
        if (picture.size[1] == height):
            y = 0
        else:
            y = random.randint(0, picture.size[1] - height)
            
        return picture.crop(
            (
                x,
                y,
                x + width,
                y + height,
            )
        )
    else:
        raise Exception('No images where found in the pictures folder!')
