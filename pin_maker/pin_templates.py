import io
import os
import requests

from lxml import etree
from PIL import Image, ImageDraw, ImageFont
from pin_maker import schemas, space_tools
from pin_maker.connectors import pb
from glob import glob
from loguru import logger
from pb_admin import schemas as pb_schemas
import random

FRAMERATE = 30
SLIDE_DURATION = 3 * FRAMERATE
TARGET_WIDTH = 1000
COMBINE_BORDER = 2

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


@logger.catch
def std_pin(product: pb_schemas.Product, len_str=800):
    """Mode can be in ('Plus', 'Premium', 'Freebie')"""
    if product.product_type == pb_schemas.ProductType.plus:
        img = Image.open(os.path.join('pin_maker', 'graph_templates', 'PlusBackgroung.png'))
        logo_img = Image.open(os.path.join('pin_maker', 'graph_templates', 'PlusLogo.png'))
    elif product.product_type == pb_schemas.ProductType.premium:
        img = Image.open(os.path.join('pin_maker', 'graph_templates', 'PremiumBackground.png'))
        logo_img = Image.open(os.path.join('pin_maker', 'graph_templates', 'PBLogo.png'))
    elif product.product_type == pb_schemas.ProductType.freebie:
        img = Image.open(os.path.join('pin_maker', 'graph_templates', 'FreebieBackground.png'))
        logo_img = Image.open(os.path.join('pin_maker', 'graph_templates', 'PBLogo.png'))
    img_draw = ImageDraw.Draw(img)
    high_point_button = 1300

    hight_title = 837
    title_rows = product.title.split()
    title_rows = make_paragraph(title_rows, len_str, TITLE_FONT)
    low_point_title = hight_title + len(title_rows) * 87
    while low_point_title > high_point_button:
        title_rows.pop()
        if not title_rows:
            break
        title_rows[-1] = title_rows[-1][:-3] + '...'
        low_point_title = hight_title + len(title_rows) * 87
    img_draw.text(
        (95, 837),
        '\n'.join(title_rows),
        fill='#000000',
        font=TITLE_FONT,
        spacing=12,
    )

    hight_description = low_point_title + 63
    description_rows = product.description.split()
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
        fill='#666666',
        font=DESCRIPTION_FONT,
        spacing=22
    )

    img_target_size_x = 1000
    img_target_size_y = 699
    preview_raw = requests.get(product.main_image_retina.original_url)
    preview_img = Image.open(io.BytesIO(preview_raw.content))
    resize_k = preview_img.size[0] / img_target_size_x
    preview_img = preview_img.resize(
        (img_target_size_x, int(preview_img.size[1] // resize_k))
    )
    if preview_img.size[1] > 669:
        preview_img = preview_img.crop((0, 0, img_target_size_x, img_target_size_y))
    img.paste(preview_img, (0, 0))
    img.paste(logo_img, (59, 598), logo_img)

    img = img.convert('RGB')
    result = io.BytesIO()
    img.save(result, 'JPEG')
    return result


@logger.catch
def resize_with_fixed_width(img, target_width):
    width_percent = (target_width / float(img.size[0]))
    new_height = int((float(img.size[1]) * float(width_percent)))
    img = img.resize((target_width, new_height))
    return img


@logger.catch
def make_glued_pin(raw_pin: schemas.ImgCombination):
    main_img_raw = requests.get(raw_pin.img_urls[0])
    main_img = Image.open(io.BytesIO(main_img_raw.content))
    main_img = resize_with_fixed_width(main_img, TARGET_WIDTH)
    for img_url in raw_pin.img_urls[1:]:
        img_raw = requests.get(img_url)
        img = Image.open(io.BytesIO(img_raw.content))
        img = resize_with_fixed_width(img, TARGET_WIDTH)
        combined_img = Image.new(
            'RGB',
            (main_img.size[0], main_img.size[1] + img.size[1] + COMBINE_BORDER),
            'white'
        )
        combined_img.paste(main_img, (0, 0))
        combined_img.paste(img, (0, main_img.height + COMBINE_BORDER))
        main_img = combined_img

    main_img = main_img.convert('RGB')
    result = io.BytesIO()
    main_img.save(result, 'JPEG')
    return result


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


def prepare_slide(slide_url: str, img_target_size_x=1000, img_target_size_y=699):
    resp = requests.get(slide_url)
    if not resp.ok:
        return
    slide_img = Image.open(io.BytesIO(resp.content))
    resize_k = slide_img.size[0] / img_target_size_x
    slide_img = slide_img.resize(
        (img_target_size_x, int(slide_img.size[1] // resize_k))
    )
    if slide_img.size[1] > img_target_size_y:
        slide_img = slide_img.crop((0, 0, img_target_size_x, img_target_size_y))
    return slide_img


def get_mask_frame():
    for filename in sorted(glob(os.path.join('pin_maker', 'graph_templates', 'transition_mask', '*.png'))):
        yield Image.open(filename)


def get_bg_frame():
    while True:
        for filename in sorted(glob(os.path.join('pin_maker', 'graph_templates', 'td_anim_bg', '*.png'))):
            yield Image.open(filename)


def get_frame_number():
    i = 0
    while True:
        yield i
        i += 1


def frame_maker(title, title_font, desc, desc_font, dir_name):
    bg = get_bg_frame()
    _title = title
    _title_font = title_font
    _desc = desc
    _desc_font = desc_font
    _dir_name = dir_name
    _i = get_frame_number()

    def inner(slide: Image):
        next_bg = next(bg)
        next_bg = write_on(
            next_bg,
            _title,
            _title_font,
            _desc,
            _desc_font,
        )
        frame = Image.new('RGB', next_bg.size)
        frame.paste(next_bg, (0, 0))
        frame.paste(slide, (0, 0))
        frame_path = os.path.join(_dir_name, f'{next(_i)}.jpg')
        frame.save(frame_path)
        return frame_path
    return inner


def write_on(
    next_bg,
    title,
    title_font,
    description,
    description_font,
    high_point_button=1300,
    hight_title=837,
    len_str=800
):
    img_draw = ImageDraw.Draw(next_bg)
    title_rows = title.split()
    title_rows = make_paragraph(title_rows, len_str, title_font)
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
        font=title_font,
        spacing=13,
    )

    hight_description = low_point_title + 60
    description_rows = description.split()
    description_rows = make_paragraph(description_rows, len_str, description_font)
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
        font=description_font,
        spacing=22
    )
    return next_bg


def make_combinations_for_glued(product: pb_schemas.Product) -> schemas.ImgCombinations:
    if product.product_type == pb_schemas.ProductType.premium:
        gallery = [img.original_url for img in product.gallery_images_retina[1:]]
    else:
        gallery = [img.original_url for img in product.gallery_images_retina]
    gallery_length = len(gallery)
    unique_combinations = schemas.ImgCombinations(combinations=[])
    if gallery_length == 0:
        unique_combinations.combinations.append(
            schemas.ImgCombination(
                img_urls=[product.main_image_retina.original_url]
            )
        )
    elif gallery_length == 1:
        unique_combinations.combinations.append(
            schemas.ImgCombination(
                img_urls=[product.main_image_retina.original_url, gallery[0]]
            )
        )
    else:
        for i in range(gallery_length):
            for j in range(i+1, gallery_length):
                combination = sorted([gallery[i], gallery[j]])
                combination = [product.main_image_retina.original_url] + combination
                if combination not in unique_combinations:
                    unique_combinations.combinations.append(
                        schemas.ImgCombination(img_urls=combination)
                    )
    unique_combinations.combinations = random.sample(
        unique_combinations.combinations,
        min(len(unique_combinations.combinations), 50)
    )
    return unique_combinations
