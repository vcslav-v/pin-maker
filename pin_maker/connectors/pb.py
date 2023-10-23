import json
import os

import requests
from loguru import logger

from pin_maker import schemas

TOKEN = os.environ.get('TOKEN', '')
PB_STAT_API_URL = os.environ.get('PB_STAT_API_URL', '')


@logger.catch
def get_product_info(url: str) -> schemas.ProductInfo:
    headers = {'Authorization': f'Basic {TOKEN}'}
    data = {'url': url}
    resp = requests.post(PB_STAT_API_URL.format(target='info'), headers=headers, json=data)
    product_info = json.loads(resp.text)
    return schemas.ProductInfo(
        pr_type=product_info['product_type'],
        url=url,
        title=product_info['title'],
        thumbnail_url=product_info['material_image_thumb'],
        thumbnail_url_x2=product_info['material_image_thumb2x'],
        main_img_url=product_info['material_image'],
        main_img_url_x2=product_info['material_image_retina'],
        gallery_urls=product_info['gallery'][:int(len(product_info['gallery'])/2)],
        gallery_retina_urls=product_info['gallery'][int(len(product_info['gallery'])/2):],
        exerpt=product_info['short_desc'],
        regular_price=product_info.get('price'),
        sale_regular_price=product_info.get('sale_price'),
        categories=[schemas.Category(name=cat['name'], url=cat['url']) for cat in product_info['categories']],
        extended_price=product_info.get('price_extended'),
        sale_extended_price=product_info.get('sale_price_extended'),
        description=str(product_info.get('description')),
        compatibilities=[schemas.Compatibility(name=comp['title'], url=comp['url']) for comp in product_info['compatibility']],
        formats=product_info['formats'][0] if isinstance(product_info['formats'][0], list) else product_info['formats']
    )
