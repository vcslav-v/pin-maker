import io
import os

import requests
from lxml import etree
from PIL import Image, ImageDraw, ImageFont
from pin_maker import schemas

TITLE_FONT = ImageFont.truetype(os.path.join('pin_maker', 'fonts', 'title.otf'), size=78)
TD_TITLE_FONT = ImageFont.truetype(os.path.join('pin_maker', 'fonts', 'TDTitle.otf'), size=80)
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


def make_pb_pin(raw_pin: schemas.Pin, len_str=800, mode='Plus'):
    """Mode can be in ('Plus', 'Premium', 'Freebie')"""
    if mode == 'Plus':
        img = Image.open(os.path.join('pin_maker', 'graph_templates', 'PlusBackgroung.png'))
        logo_img = Image.open(os.path.join('pin_maker', 'graph_templates', 'PlusLogo.png'))
    elif mode == 'Premium':
        img = Image.open(os.path.join('pin_maker', 'graph_templates', 'PremiumBackground.png'))
        logo_img = Image.open(os.path.join('pin_maker', 'graph_templates', 'PBLogo.png'))
    elif mode == 'Freebie':
        img = Image.open(os.path.join('pin_maker', 'graph_templates', 'FreebieBackground.png'))
        logo_img = Image.open(os.path.join('pin_maker', 'graph_templates', 'PBLogo.png'))
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

    img_target_size_x = 1000
    img_target_size_y = 699
    preview_raw = requests.get(raw_pin.img_url)
    preview_img = Image.open(io.BytesIO(preview_raw.content))
    resize_k = preview_img.size[0] / img_target_size_x
    preview_img = preview_img.resize(
        (img_target_size_x, int(preview_img.size[1] // resize_k)),
        Image.ANTIALIAS,
    )
    if preview_img.size[1] > 669:
        preview_img = preview_img.crop((0, 0, img_target_size_x, img_target_size_y))
    img.paste(preview_img, (0, 0))
    img.paste(logo_img, (59, 598), logo_img)

    result = io.BytesIO()
    img.save(result, 'PNG')
    return result.getvalue()


def make_td_pin(raw_pin: schemas.Pin, len_str=800):
    high_point_button = 1325
    img = Image.open(os.path.join('pin_maker', 'graph_templates', 'TDBackground.png'))
    img_draw = ImageDraw.Draw(img)

    hight_title = 837
    title_rows = raw_pin.title.split()
    title_rows = make_paragraph(title_rows, len_str, TD_TITLE_FONT)
    low_point_title = hight_title + len(title_rows) * 87
    while low_point_title > high_point_button:
        title_rows.pop()
        if not title_rows:
            break
        title_rows[-1] = title_rows[-1][:-3] + '...'
        low_point_title = hight_title + len(title_rows) * 87
    img_draw.text(
        (100, hight_title),
        '\n'.join(title_rows),
        fill='#000000',
        font=TD_TITLE_FONT,
        spacing=13,
    )

    hight_description = low_point_title + 60
    description_rows = raw_pin.description.split()
    description_rows = make_paragraph(description_rows, len_str, DESCRIPTION_FONT)
    low_point_desc = hight_description + len(description_rows) * 50 
    while low_point_desc > high_point_button:
        description_rows.pop()
        if not description_rows:
            break
        description_rows[-1] = description_rows[-1][:-3] + '...'
        low_point_desc = hight_description + len(description_rows) * 50
    img_draw.text(
        (100, hight_description),
        '\n'.join(description_rows),
        fill='#000000',
        font=DESCRIPTION_FONT,
        spacing=22
    )

    img_target_size_x = 1000
    img_target_size_y = 699
    preview_raw = requests.get(raw_pin.img_url)
    preview_img = Image.open(io.BytesIO(preview_raw.content))
    resize_k = preview_img.size[0] / img_target_size_x
    preview_img = preview_img.resize(
        (img_target_size_x, int(preview_img.size[1] // resize_k)),
        Image.ANTIALIAS,
    )
    if preview_img.size[1] > 669:
        preview_img = preview_img.crop((0, 0, img_target_size_x, img_target_size_y))
    img.paste(preview_img, (0, 0))

    result = io.BytesIO()
    img.save(result, 'PNG')
    return result.getvalue()


def _get_disc_text(disc_elem):
    disc_text = ''
    inner_disc_spans = disc_elem[-1].xpath('.//span')
    if inner_disc_spans:
        disc_text = ''.join([inner_disc_span.text for inner_disc_span in inner_disc_spans])
    else:
        disc_text = disc_elem[-1].text.strip() if disc_elem[-1].text else ''
    return disc_text


def get_raw_pins(link: str) -> schemas.PinList:
    result = schemas.PinList(pins=[])
    resp = requests.get(link)
    dom = etree.HTML(resp.content)
    item_containers = dom.xpath(
        '//div[@data-widget_type="button.default"][contains(.,"Download Now")]/..'
    )
    for item_container in item_containers:
        img = item_container.xpath('.//img')
        item_link = item_container.xpath('.//a[contains(.,"Download Now")]') or (
            item_container.xpath('.//a[contains(.,"Free Download")]')
        )
        disc = item_container.xpath('.//p') or (
            item_container.xpath('.//div[contains(@class, "elementor-text-editor")]')
        )
        title = item_container.xpath('.//h3')
        if img and item_link and disc and title and title:
            disc_text = _get_disc_text(disc)
            img_src = img[-1].attrib.get('src')
            link_href = item_link[-1].attrib.get('href')
            title_text = title[-1].text.strip() if title[-1].text else ''
            if img_src and link_href and title_text and disc_text:
                result.pins.append(
                    schemas.Pin(
                        img_url=img_src,
                        title=title[-1].text.strip(),
                        description=disc_text if len(disc_text) < 500 else f'{disc_text[:497]}...',
                        link=link_href,
                    )
                )
    return result
