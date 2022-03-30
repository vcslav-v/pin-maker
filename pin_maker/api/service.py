import io
import os

import requests
from PIL import Image, ImageDraw, ImageFont
from pin_maker import schemas

TITLE_FONT = ImageFont.truetype(os.path.join('pin_maker', 'fonts', 'title.otf'), size=78)
DESCRIPTION_FONT = ImageFont.truetype(os.path.join('pin_maker', 'fonts', 'paragraph.ttf'), size=32)


def make_paragraph(row, len_str, font):
    next_row = []
    while font.getlength(' '.join(row)) > len_str:
        next_row.append(row.pop())
    next_row.reverse()
    if not row:
        row.append(next_row.pop(0))
    result = [' '.join(row)]
    if next_row:
        result.extend(make_paragraph(next_row, len_str, font))
    return result


def make_plus_pin(raw_pin: schemas.Pin, len_str=800):
    img = Image.open(os.path.join('pin_maker', 'graph_templates', 'Backgroung.png'))
    logo_img = Image.open(os.path.join('pin_maker', 'graph_templates', 'PlusLogo.png'))
    img_draw = ImageDraw.Draw(img)

    hight_title = 837
    title_rows = raw_pin.title.split()
    title_rows = make_paragraph(title_rows, len_str, TITLE_FONT)
    img_draw.text(
        (95, 837),
        '\n'.join(title_rows),
        fill='#000000',
        font=TITLE_FONT,
        spacing=12,
    )

    hight_description = hight_title + len(title_rows) * 87 + 63
    description_rows = raw_pin.description.split()
    description_rows = make_paragraph(description_rows, len_str, DESCRIPTION_FONT)
    img_draw.text(
        (100, hight_description),
        '\n'.join(description_rows),
        fill='#666666',
        font=DESCRIPTION_FONT,
        spacing=22
    )


    preview_raw = requests.get(raw_pin.img_url)
    preview_img = Image.open(io.BytesIO(preview_raw.content))
    resize_k = preview_img.size[0] / 1000
    preview_img = preview_img.resize((1000, int(preview_img.size[1] // resize_k)), Image.ANTIALIAS)
    preview_img = preview_img.crop((0, 0, 1000, 669))
    img.paste(preview_img, (0, 0))
    img.paste(logo_img, (59, 598), logo_img)

    result = io.BytesIO()
    img.save(result, 'PNG')
    return result.getvalue()
