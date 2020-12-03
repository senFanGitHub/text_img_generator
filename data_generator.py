import os
import random

from PIL import Image, ImageFilter

import computer_text_generator
import background_generator
import distorsion_generator
import numpy as np
try:
    import handwritten_text_generator
except ImportError as e:
    print('Missing modules for handwritten text generation.')


class FakeTextDataGenerator(object):
    @classmethod
    def generate_from_tuple(cls, t):
        """
            Same as generate, but takes all parameters as one tuple
        """

        res = cls.generate(*t)
        return res

    @classmethod
#         def generate(cls, index, text, font, out_dir, size, extension, skewing_angle, random_skew, blur, random_blur, background_type, distorsion_type, distorsion_orientation, is_handwritten, name_format, width, alignment, text_color, orientation, space_width, margins, fit):
    def generate(cls, index, text, font, out_dir, size, extension,distorsion_orientation, name_format, width, alignment, text_color,  space_width, margins, fit,record):
        ### inital:
        random_skew = True
        random_blur = True
        distorsion_orientation =0

        gbklen=0
        for c in text:
            try:
                cc=c.encode('gbk')
                gbklen=gbklen+len(cc)
            except:
                gbklen=gbklen+1
                continue

        ## 随机背景__高斯多数
        background_type = random.randint(1,100)

        
        ## 随机颜色 黑色多些
        font_colors = ['#660066', '#003366', '#008000', '#ffd700', '#ffa500', '#0066dc', '#ffc3a0', '#079fab', '#ab07a5', '#7e082a', '#710c4c', '#6c78a7', '#6c78a7', '#a3ff00', '#7fffd4', '#ff9ca6', '#4b3621', '#60aef6', '#190533', '#450e3e']
        use_color = random.randint(1,3)
        color_used = random.randint(0,len(font_colors)-1)
        if background_type==3:
            use_color=3
#         if use_color==3:
#             text_color=font_colors[color_used]
    

        # 随机扭曲——正常的占多数
        distorsion_type = random.randint(-5,5)

        ## 随机模糊——清晰的占多数, 若背景为图，模糊减弱
        p_bl= random.randint(0,10)
        if p_bl > 7:
            blur =1
            random_blur = True
        else :
            blur =0
        
        if background_type==3:
            blur =0
            
        ## 随机倾斜——正常的占多数
        
        p_rk= random.randint(0,10)
        if p_rk > 7:
            skewing_angle =3
            random_skew = True
        else :
            skewing_angle = 0
                        
        ## 是否相切
        p_fit= random.randint(0,7)
        if p_fit<=4:
            fit = True
        else :
            fit =False
        
        ## margin: 随机左右margin 
        margin_top, margin_left, margin_bottom, margin_right = margins
        p_mar= random.randint(0,6)
        if p_mar>=4:
            margin_left = random.randint(1,50)
            margin_right = random.randint(1,50)
            margin_top = random.randint(-10,-1)
            margin_bottom = random.randint(-10,-1)
        
        image = None

        horizontal_margin = margin_left + margin_right
        vertical_margin = margin_top + margin_bottom

        ##########################
        # Create picture of text #
        ##########################

        image ,mask= computer_text_generator.generate(text, font, text_color, size, space_width, fit)
        negtive_img,negtive_mask= computer_text_generator.generate('卷积神经网络实践', font, text_color, size, space_width, fit)
        
        
        

        
        if image==None:
            return 0
        
        
        random_angle = random.randint(0-skewing_angle, skewing_angle)
        

        def proc(image,size,tag):
            rotated_img = image.rotate(skewing_angle if not random_skew else random_angle, expand=1)

            #############################
            # Apply distorsion to image #
            #############################
            if distorsion_type <= 0:
                distorted_img = rotated_img # Mind = blown
            elif distorsion_type == 1:
                distorted_img = distorsion_generator.sin(
                    rotated_img,
                    vertical=(distorsion_orientation == 0 or distorsion_orientation == 2),
                    horizontal=(distorsion_orientation == 1 or distorsion_orientation == 2)
                )
            elif distorsion_type == 2:
                distorted_img = distorsion_generator.cos(
                    rotated_img,
                    vertical=(distorsion_orientation == 0 or distorsion_orientation == 2),
                    horizontal=(distorsion_orientation == 1 or distorsion_orientation == 2)
                )
            else:
                distorted_img = distorsion_generator.random(
                    rotated_img,
                    vertical=(distorsion_orientation == 0 or distorsion_orientation == 2),
                    horizontal=(distorsion_orientation == 1 or distorsion_orientation == 2)
                )

            ##################################
            # Resize image to desired format #
            ##################################

            # Horizontal text
    #         if orientation == 0:
            new_width=0
            try:
                new_width = int(distorted_img.size[0] * (float(size - vertical_margin) / float(distorted_img.size[1])))
            except:
                print(text)

            ## 保证大概比例
            l = int(gbklen/2+0.5)*28 

            size = int((new_width+ horizontal_margin)*size/l)



            resized_img = distorted_img.resize((new_width, size - vertical_margin), Image.ANTIALIAS)
            background_width = width if width > 0 else new_width + horizontal_margin
            background_height = size


            #############################
            # Generate background image #
            #############################


            if background_type <=50:
                background = background_generator.gaussian_noise(background_height, background_width)
            elif (background_type> 50) and (background_type<=70) :
                background = background_generator.plain_white(background_height, background_width)
            elif (background_type> 70) and (background_type<=75) :
                background = background_generator.quasicrystal(background_height, background_width)
            else:
                background = background_generator.picture(background_height, background_width,text_color)



            if 'mask' in tag:
                background = background_generator.plain_white(background_height, background_width)
            else :
                 background = background_generator.picture(background_height, background_width,text_color)
            #############################
            # Place text with alignment #
            #############################

            new_text_width, _ = resized_img.size

            if alignment == 0 or width == -1:
                background.paste(resized_img, (margin_left, margin_top), resized_img)
            elif alignment == 1:
                background.paste(resized_img, (int(background_width / 2 - new_text_width / 2), margin_top), resized_img)
            else:
                background.paste(resized_img, (background_width - new_text_width - margin_right, margin_top), resized_img)

            ##################################
            # Apply gaussian blur #
            ##################################

            final_image = background.filter(
                ImageFilter.GaussianBlur(
                    radius=(blur if not random_blur else random.randint(0, blur))
                )
            )

            #####################################
            # Generate name for resulting image #
            #####################################
            if name_format == 0:
                image_name = '{}_{}.{}'.format(text, str(index), extension)
            elif name_format == 1:
                image_name = '{}_{}.{}'.format(str(index), text, extension)
            elif name_format == 2:
                image_name = '{}_{}.{}'.format(record,str(index),extension)
            else:
                print('{} is not a valid name format. Using default.'.format(name_format))
                image_name = '{}_{}.{}'.format(text, str(index), extension)

            # Save the image
            final_image.convert('RGB').save(os.path.join(out_dir,tag+ image_name))
        
        proc(mask,size,'mask')
        proc(image,size,'img')
    
        proc(negtive_mask,size,'negtive_mask')
        proc(negtive_img,size,'negtive_img')
        return 1