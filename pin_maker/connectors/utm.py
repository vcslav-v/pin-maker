import requests
from loguru import logger
from pin_maker import schemas
from pin_maker.config import UTM_API_TOKEN, UTM_API_URL, UTM_API_USER


@logger.catch
def get_utm(
    url: str,
    product_type: str,
    campaning_dop: str = '0',
) -> str:
    with requests.Session() as session:
        session.auth = ('api', UTM_API_TOKEN)
        data = schemas.LinkCreate(
            target_url=url,
            source='pinterest',
            medium='social',
            campaign_project='pb',
            campaning_dop=campaning_dop,
            content='0',
            term_material=product_type,
            term_page='item',
            user=UTM_API_USER,
        )
    resp = session.post(f'{UTM_API_URL}/api/create_link', data=data.model_dump_json().encode('utf-8'))
    resp.raise_for_status()
    utm_link = schemas.Link.model_validate_json(resp.content)
    return utm_link.full_url
