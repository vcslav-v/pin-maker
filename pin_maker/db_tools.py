from pin_maker import db, models, schemas
from pin_maker.config import logger
import json
from pb_admin import schemas as pb_schemas
from random import randint
from sqlalchemy import func
import uuid


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
            template_task = schemas.PinTask(
                template_name=db_template.name,
                products=[],
            )
            db_template_pin_product_ids = session.query(
                models.Pin.product_id
            ).filter_by(template_id=db_template.id).all()
            db_template_pin_product_ids = [
                db_template_pin_product_id[0] for db_template_pin_product_id in db_template_pin_product_ids
            ]
            db_template_pin_product_ids = set(db_template_pin_product_ids)
            for product in products:
                if product.ident not in db_template_pin_product_ids:
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
            product_url=f'{product.url}/?r={uuid.uuid4().hex[:8]}',
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
                db_new_pin.order = randint(max_order, max_order + len(db_new_pins))
            session.commit()
