import pathlib
import click
import math
from PIL import Image
from typing import Union, List, Generator
from pathlib import Path


ASCII_CHARS = ["@", "#", "$", "%", "?", "*", "+", ";", ":", ",", ".", " "]


def resize_image(image: Image.Image, width_new: int = 100, char_ratio=1.65):
    """Resize image while maintaining aspect ratio and reduce height according to char_ratio

    Args:
        image (Image): Pillow image
        width_new (int): Width to resize to
        char_ratio (float): Ratio of height/width of an ascii character (Characters are usually higher than their width)
    """
    width, height = image.size
    ratio = height / width / char_ratio
    height_new = int(width_new * ratio)
    image_resized = image.resize((width_new, height_new))
    return image_resized


def grayscaler(image: Image.Image):
    """Convert pillow image into grayscale

    Args:
        image (Image): Image to convert
    """
    gray_im = image.convert("L")
    return gray_im


def format_ascii_img(char_array: Union[List, Generator], width: int):
    """Format list or generator of ascii chars with newlines based on the image's width

    Args:
        char_array (Union[List, Generator]): List or generator of characters
        width (int): Image width
    """
    text_list = []
    px_num: int = 1
    for c in char_array:
        if px_num % width == 0:
            text_list.append(f"{c}\n")
        else:
            text_list.append(c)
        px_num += 1
    return "".join(text_list)


def map_pixels_to_text(image: Image.Image, invert=False):
    """Map each pixels of an image into ascii characters based on ASCII_CHARS

    Args:
        image (Image): Grayscaled pillow image
        invert (bool): Invert the ASCII_CHARS array
    """
    if image.mode is not "L":
        raise ValueError("Image must be grayscale!")
    width = image.width
    pixels = image.getdata()
    a_chars = ASCII_CHARS if not invert else list(reversed(ASCII_CHARS))
    # ascii_div is the range value that a single char inside ASCII_CHARS has. 255 being the max grayscale value
    ascii_div = math.ceil(255 / len(a_chars))
    # print(ascii_div)
    char_iter = (a_chars[int(pixel//ascii_div)] for pixel in pixels)
    text = format_ascii_img(char_iter, width)
    return text


@click.command()
@click.argument("image_path")
@click.option("-w", "--width", default=100, help="Resized width of image, defaults to 100.")
@click.option("-c", "--char-ratio", default=2.0, help="Height/width ratio of a character, defaults to 2.")
@click.option("--invert", is_flag=True, help="Inverses the contrast.")
def main(image_path, width, char_ratio, invert):
    abs_path = Path(image_path).resolve()
    im_name = abs_path.stem
    im = Image.open(abs_path)
    im = grayscaler(resize_image(im, width_new=width, char_ratio=char_ratio))
    text = map_pixels_to_text(im, invert)
    with open(f"./images/renders/{im_name}.txt", "w") as f:
        f.write(text)


if __name__ == "__main__":
    main()
