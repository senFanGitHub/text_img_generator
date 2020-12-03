import argparse
import os, errno
import random
import string

from tqdm import tqdm
from string_generator import create_strings_from_file

from data_generator import FakeTextDataGenerator
from multiprocessing import Pool

def margins(margin):
    margins = margin.split(',')
    if len(margins) == 1:
        return [margins[0]] * 4
    return [int(m) for m in margins]

def parse_arguments():
    """
        Parse the command line arguments of the program.
    """
    parser = argparse.ArgumentParser(description='Generate synthetic text data for text recognition.')
    parser.add_argument(
        "--output_dir",
        type=str,
        nargs="?",
        help="The output directory",
        default="MASK_demo/",
    )
    parser.add_argument(
        "-i",
        "--input_file",
        type=str,
        nargs="?",
        help="When set, this argument uses a specified text file as source for the text",
        default=""
    )
    parser.add_argument(
        "-l",
        "--language",
        type=str,
        nargs="?",
        help="The language to use, should be fr (French), en (English), es (Spanish), de (German), or cn (Chinese).",
        default="sim"
    )
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        nargs="?",
        help="The number of images to be created.",
        default=100
    )

    parser.add_argument(
        "-f",
        "--format",
        type=int,
        nargs="?",
        help="Define the height of the produced images if horizontal, else the width",
        default=32,
    )
    parser.add_argument(
        "-t",
        "--thread_count",
        type=int,
        nargs="?",
        help="Define the number of thread to use for image generation",
        default=8,
    )
    parser.add_argument(
        "-e",
        "--extension",
        type=str,
        nargs="?",
        help="Define the extension to save the image with",
        default="jpg",
    )


    parser.add_argument(
        "-na",
        "--name_format",
        type=int,
        help="Define how the produced files will be named. 0: [TEXT]_[ID].[EXT], 1: [ID]_[TEXT].[EXT] 2: [ID].[EXT] + one file labels.txt containing id-to-label mappings",
        default=2,
    )

    parser.add_argument(
        "-do",
        "--distorsion_orientation",
        type=int,
        nargs="?",
        help="Define the distorsion's orientation. Only used if -d is specified. 0: Vertical (Up and down), 1: Horizontal (Left and Right), 2: Both",
        default=0
    )
    parser.add_argument(
        "-wd",
        "--width",
        type=int,
        nargs="?",
        help="Define the width of the resulting image. If not set it will be the width of the text + 10. If the width of the generated text is bigger that number will be used",
        default=-1
    )
    parser.add_argument(
        "-al",
        "--alignment",
        type=int,
        nargs="?",
        help="Define the alignment of the text in the image. Only used if the width parameter is set. 0: left, 1: center, 2: right",
        default=1
    )

    parser.add_argument(
        "-tc",
        "--text_color",
        type=str,
        nargs="?",
        help="Define the text's color, should be either a single hex color or a range in the ?,? format.",
        default='#282828'
    )
    parser.add_argument(
        "-sw",
        "--space_width",
        type=float,
        nargs="?",
        help="Define the width of the spaces between words. 2.0 means twice the normal space width",
        default=1.0
    )
    parser.add_argument(
        "-m",
        "--margins",
        type=margins,
        nargs="?",
        help="Define the margins around the text when rendered. In pixels",
        default=(0, 0, 2, 2)
    )
    parser.add_argument(
        "-fi",
        "--fit",
        action="store_true",
        help="Apply a tight crop around the rendered text",
        default=True
    )


    return parser.parse_args()



def load_fonts(lang):
    """
        Load all fonts in the fonts directories
    """

    if lang == 'tra':
        return [os.path.join('fonts/cn_繁体都正常', font) for font in os.listdir('fonts/cn_繁体都正常')]
    elif lang == 'sim':
        return [os.path.join('fonts/cn_简体都正常', font) for font in os.listdir('fonts/cn_简体都正常')]

def main():
    """
        Description: Main function
    """

    # Argument parsing
    args = parse_arguments()

    # Create the directory if it does not exist.
    try:
        os.makedirs(args.output_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    
    record = args.input_file.split('/')[-1].replace('.txt','')
    print(record)

    # Create font (path) list
    fonts = load_fonts(args.language)
    print(args.language)
    # Creating synthetic sentences (or word)
    strings = []
    
    strings = create_strings_from_file(args.input_file, args.count)

    string_count = len(strings)

    p = Pool(args.thread_count)
    string_count_res=[]
    for res in tqdm(p.imap (
        FakeTextDataGenerator.generate_from_tuple,
        zip(
            [i for i in range(0, string_count)],
            strings,
            [fonts[random.randrange(0, len(fonts))] for _ in range(0, string_count)],
            [args.output_dir] * string_count,
            [args.format] * string_count,
            [args.extension] * string_count,
            [args.distorsion_orientation] * string_count,
            [args.name_format] * string_count,
            [args.width] * string_count,
            [args.alignment] * string_count,
            [args.text_color] * string_count,
            [args.space_width] * string_count,
            [args.margins] * string_count,
            [args.fit] * string_count,
            [record]*string_count
        )
    ), total=args.count):
        string_count_res.append(res)
        pass
    p.terminate()

    if args.name_format == 2:
        # Create file with filename-to-label connections
        with open(os.path.join(args.output_dir, "{}_labels.txt".format(record)), 'w', encoding="utf8") as f:
            for i in range(string_count):
                if string_count_res[i]==0:
                    continue
                file_name = str(i) + "." + args.extension
                f.write("{}_{} {}\n".format(record,file_name, strings[i]))

if __name__ == '__main__':
    main()
