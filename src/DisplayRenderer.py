import adafruit_rgb_display.st7735 as st7735
import RPi.GPIO as GPIO
from PIL import Image, ImageColor, ImageDraw, ImageFont, ImageOps
from const import MESSAGE_CHAR_LENGTH, FONT_FAMILY
from image_utils import ImageText


class DisplayRenderer:
    def __init__(self, display):
        self.display = display
        self.display.fill(0)

    def get_swaped_rdb(self, hex_color: str):
        rgb = ImageColor.getrgb(str("#" + hex_color))
        # need to swap r and b channel: (see https://github.com/adafruit/Adafruit-ST7735-Library/issues/86#issuecomment-519164816)
        return (rgb[2], rgb[1], rgb[0])

    def draw_message_text(self, text: str, author: str, text_color: str = "ffffff", bg_color: str = "000000"):
        text_rgb = self.get_swaped_rdb(text_color)
        bg_rgb = self.get_swaped_rdb(bg_color)
        width, height = self._display_dimensions()
        default_font_size = 14
        font = ImageFont.truetype(FONT_FAMILY, default_font_size)

        image = Image.new("RGB", (width, height), bg_rgb)
        image_text = ImageText(image)

        chars = len(text)
        fontsize = 13
        if chars >= 120 and chars <= MESSAGE_CHAR_LENGTH:
            fontsize = 12
        elif chars > 80 and chars <= 120:
            fontsize = 13
        elif chars > 50 and chars <= 80:
            fontsize = 15
        elif chars <= 50:
            fontsize = 18

        image_text.write_multi_line_text_box(
            (2, -12),
            text,
            box_width=width - 2,
            font_filename=FONT_FAMILY,
            font_size=fontsize,
            color=text_rgb,
            justify_last_line=False,
        )

        author_text = "from " + author
        author_text_size_x, author_text_size_y = image_text.draw.textsize(
            author_text, font=font
        )
        image_text.write_text(
            (2, height - author_text_size_y - 2),
            author_text,
            font_filename=FONT_FAMILY,
            font_size="fill",
            max_height=default_font_size,
            max_width=width - 2,
            color=text_rgb,
        )

        self.display.image(image_text.image)

    def draw_multi_line_center_text(self, text: str, font_size: int = 16, text_color : str = "white"):
        width, height = self._display_dimensions()
        image, draw = self._get_draw()

        image_text = ImageText(image)
        image_text.write_multi_line_text_box(
            (0, 0),
            text=text,
            box_width=width - 2,
            font_filename=FONT_FAMILY,
            font_size=font_size,
            color=text_color,
            place="center",
            position="middle",
        )

        self.display.image(image_text.image)

    def draw_center_text(self, text: str, font_size: int = 16, text_color : str = "white"):
        width, height = self._display_dimensions()
        image, draw = self._get_draw()

        font = ImageFont.truetype(FONT_FAMILY, font_size)
        
        textWidth, textHeight = draw.textsize(text, font=font)
        screen_x  = (width - textWidth) / 2
        screen_y = (height - textHeight) / 2

        draw.text((screen_x, screen_y), text, font=font, fill=text_color)

        self.display.image(image)

    def _center_text(self, draw, text: str, font: ImageFont, text_color: str = "white") -> ImageFont:
        width, height = self._display_dimensions()
        textWidth, textHeight = draw.textsize(text, font=font)
        
        center_x = (width - textWidth) / 2
        center_y = (height - textHeight) / 2
        draw.text((center_x, center_y), text, font=font, fill=text_color)
        
        return draw

    def _display_dimensions(self):
        if self.display.rotation % 180 == 90:
            height = self.display.width
            width = self.display.height
        else:
            width = self.display.width
            height = self.display.height

        return width, height

    def _get_draw(self):
        width, height = self._display_dimensions()
        
        image = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(image)
        
        return image, draw