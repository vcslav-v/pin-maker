from pin_maker import db, models, schemas
from pin_maker.config import logger
import json
from pb_admin import schemas as pb_schemas
from random import randint
from sqlalchemy import func
import uuid
from pin_maker.config import MAIN_BOARD_NAME, FREEBIES_BOARD_NAME, PLUS_BOARD_NAME, PREMIUM_BOARD_NAME, REF_CODE

from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


def _prepare_url(url: str, new_params: dict) -> str:
    # TODO: move it to pb_admin
    parsed_url = urlparse(url)
    params = parse_qs(parsed_url.query)
    params.update(new_params)
    query_string = urlencode(params, doseq=True)
    new_url = urlunparse(
        (parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, query_string, parsed_url.fragment)
    )
    return new_url


def get_cookies() -> list:
    '''Get cookies from db.'''
    with db.SessionLocal() as session:
        db_info = session.query(models.Info).first()
        if not db_info:
            return []

        db_cookies = db_info.pinterest_cookies
        if not db_cookies:
            return []
        db_cookies = json.loads(db_cookies)
        return db_cookies.get('cookies', [])


def update_cookies(cookies: list):
    '''Update cookies in db.'''
    with db.SessionLocal() as session:
        db_info = session.query(models.Info).first()
        if not db_info:
            db_info = models.Info()
            session.add(db_info)

        db_info.pinterest_cookies = json.dumps({'cookies': cookies})
        session.commit()


def get_new_tasks(products: list[pb_schemas.Product]) -> list[schemas.PinTask]:
    with db.SessionLocal() as session:
        db_templates = session.query(models.Template).all()
        result = []
        for db_template in db_templates:
            db_no_format_products = session.query(
                models.NoFormatProduct.product_id,
                models.NoFormatProduct.product_type,
            ).filter_by(
                template_id=db_template.id
            ).all()

            template_task = schemas.PinTask(
                template_name=db_template.name,
                products=[],
            )
            db_template_pin_products = session.query(
                models.Pin.product_id,
                models.Pin.product_type,
            ).filter_by(template_id=db_template.id).all()
            for product in products:
                if (product.ident, product.product_type) in db_no_format_products:
                    continue
                if (product.ident, product.product_type) not in db_template_pin_products:
                    template_task.products.append(product)
            result.append(template_task)
        return result


def save_pin_task(product: pb_schemas.Product, pin_description: str, pin_key_words: str, img_space_key: str, template_name: str):
    with db.SessionLocal() as session:
        db_template = session.query(models.Template).filter_by(name=template_name).first()
        if not db_template:
            logger.error(f'No template with name {template_name}')
            return
        db_pin = models.Pin(
            product_id=product.ident,
            product_type=product.product_type,
            product_url=_prepare_url(product.url, {
                'ref': REF_CODE,
                'r': uuid.uuid4().hex[:8],
            }),
            template_id=db_template.id,
            media_do_key=img_space_key,
            title=product.title,
            description=pin_description,
            key_words=pin_key_words,
        )
        session.add(db_pin)
        session.commit()


def order_new_pins():
    with db.SessionLocal() as session:
        db_templates = session.query(models.Template).all()
        for db_template in db_templates:
            db_new_pins = session.query(models.Pin).filter_by(template_id=db_template.id)
            db_new_pins = db_new_pins.filter_by(order=None).all()
            max_order = session.query(func.max(models.Pin.order))
            max_order = max_order.filter_by(template_id=db_template.id).scalar()
            if not max_order:
                max_order = 0
            for db_new_pin in db_new_pins:
                logger.info(f'Ordering pin {db_new_pin.id}')
                db_new_pin.order = randint(max_order, max_order + len(db_new_pins))
                session.commit()
                logger.info(f'Left {len(db_new_pins) - db_new_pins.index(db_new_pin)} pins to order')


def get_pins_for_day() -> list[schemas.PinRow]:
    with db.SessionLocal() as session:
        db_templates = session.query(models.Template).all()
        result = []
        for db_template in db_templates:
            db_pins = session.query(models.Pin).filter_by(template_id=db_template.id)
            db_pins = db_pins.filter_by(on_main_board=False)
            db_pins = db_pins.order_by(models.Pin.order).limit(db_template.pin_limit_per_day).all()
            for db_pin in db_pins:
                result.append(schemas.PinRow(
                    db_ident=db_pin.id,
                    title=db_pin.title,
                    media_key=db_pin.media_do_key,
                    description=db_pin.description,
                    link=db_pin.product_url,
                    key_words=db_pin.key_words,
                    board=MAIN_BOARD_NAME
                ))
        for db_template in db_templates:
            db_pins = session.query(models.Pin).filter_by(template_id=db_template.id)
            db_pins = db_pins.filter_by(on_special_board=False, on_main_board=True)
            db_pins = db_pins.order_by(models.Pin.order).all()
            for db_pin in db_pins:

                if db_pin.product_type == pb_schemas.ProductType.freebie:
                    _board = FREEBIES_BOARD_NAME
                elif db_pin.product_type == pb_schemas.ProductType.plus:
                    _board = PLUS_BOARD_NAME
                elif db_pin.product_type == pb_schemas.ProductType.premium:
                    _board = PREMIUM_BOARD_NAME

                result.append(schemas.PinRow(
                    db_ident=db_pin.id,
                    title=db_pin.title,
                    media_key=db_pin.media_do_key,
                    description=db_pin.description,
                    link=db_pin.product_url,
                    key_words=db_pin.key_words,
                    board=_board
                ))
        return result


def mark_pins_as_done(pins: list[schemas.PinRow]):
    with db.SessionLocal() as session:
        for pin in pins:
            db_pin = session.query(models.Pin).filter_by(id=pin.db_ident).first()
            if not db_pin:
                continue
            if pin.board == MAIN_BOARD_NAME:
                db_pin.on_main_board = True
            elif pin.board == FREEBIES_BOARD_NAME or pin.board == PLUS_BOARD_NAME or pin.board == PREMIUM_BOARD_NAME:
                db_pin.on_special_board = True
            session.commit()


def get_previous_pins_space_keys() -> list[str]:
    with db.SessionLocal() as session:
        db_pins = session.query(models.Pin.media_do_key).filter_by(on_main_board=True, on_special_board=True)
        db_pins = db_pins.all()
        return [db_pin[0] for db_pin in db_pins]


def save_no_format_product(product: pb_schemas.Product, template_name: str):
    with db.SessionLocal() as session:
        template = session.query(models.Template).filter_by(name=template_name).first()
        session.add(models.NoFormatProduct(
            product_id=product.ident,
            product_type=product.product_type,
            template_id=template.id,
        ))
        session.commit()
