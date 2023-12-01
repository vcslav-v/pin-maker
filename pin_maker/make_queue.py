from pin_maker import db_tools, pin_templates, pinterest, schemas, space_tools
from pin_maker.config import (
    COLLAGE_TEMPLATE_NAME,
    PB_LOGIN,
    PB_PASSWORD,
    SITE_URL,
    STANDARD_TEMPLATE_NAME,
    logger,
)
from pb_admin import schemas as pb_schemas
import pb_admin
from bs4 import BeautifulSoup
import uuid


def _remove_html_tags(html: str) -> str:
    """Remove html tags from text."""
    soup = BeautifulSoup(html, 'html.parser')
    text = ' '.join(soup.get_text().split())
    return text


def _make_std_template(product: pb_schemas.Product, all_tags: list[pb_schemas.Tag], pb_session: pb_admin.PbSession):
    """Make pins by std template."""
    logger.info(f'Getting product {product.ident}...')
    full_product = pb_session.products.get(product.ident, product.product_type)
    full_product.description = _remove_html_tags(full_product.description)
    if not full_product.is_live \
            or not full_product.main_image_retina \
            or not full_product.title \
            or not full_product.description \
            or not full_product.slug \
            or not full_product.url:
        logger.info(f"Product {product.ident} isn't in format.")
        db_tools.save_no_format_product(product, STANDARD_TEMPLATE_NAME)
        return
    logger.info(f'Got product {product.ident}.')
    logger.info('Getting image...')
    img_file = pin_templates.std_pin(full_product)
    logger.info('Saving image.')
    img_space_key = space_tools.save_to_space(
        img_file.getvalue(),
        STANDARD_TEMPLATE_NAME,
        f'{product.slug}.jpg'
    )
    img_file.close()
    logger.info('Making pin info.')
    _tags = [tag for tag in all_tags if tag.ident in full_product.tags_ids]
    pin_description = pinterest.make_description(_tags, full_product.description)
    key_words = ', '.join([tag.name for tag in _tags])
    logger.info('Saving pin info.')
    db_tools.save_pin_task(
        full_product,
        pin_description,
        key_words,
        img_space_key,
        STANDARD_TEMPLATE_NAME
    )
    logger.info(f'Pin for product {product.ident} is made.')


def _make_collage_template(product: pb_schemas.Product, all_tags: list[pb_schemas.Tag], pb_session: pb_admin.PbSession):
    """Make pins by collage template."""
    logger.info(f'Getting product {product.ident}...')
    full_product = pb_session.products.get(product.ident, product.product_type)
    full_product.description = _remove_html_tags(full_product.description)
    if not full_product.is_live \
            or not full_product.main_image_retina \
            or not full_product.title \
            or not full_product.description \
            or not full_product.slug \
            or not full_product.url:
        logger.info(f"Product {product.ident} isn't in format.")
        db_tools.save_no_format_product(product, COLLAGE_TEMPLATE_NAME)
        return
    logger.info(f'Got product {product.ident}.')
    logger.info('Making images combinations...')
    img_combinations = pin_templates.make_combinations_for_glued(full_product)
    logger.info(f'Got {len(img_combinations.combinations)} combinations.')
    logger.info('Making pin info.')
    _tags = [tag for tag in all_tags if tag.ident in full_product.tags_ids]
    pin_description = pinterest.make_description(_tags, full_product.description)
    key_words = ', '.join([tag.name for tag in _tags])
    for img_combination in img_combinations.combinations:
        logger.info('Making image...')
        img_file = pin_templates.make_glued_pin(img_combination)
        logger.info('Saving image.')
        img_space_key = space_tools.save_to_space(
            img_file.getvalue(),
            COLLAGE_TEMPLATE_NAME,
            f'{product.slug}_{uuid.uuid4().hex[:8]}.jpg'
        )
        img_file.close()
        logger.info('Saving pin info.')
        db_tools.save_pin_task(
            full_product,
            pin_description,
            key_words,
            img_space_key,
            COLLAGE_TEMPLATE_NAME
        )
        logger.info(f'Left {len(img_combinations.combinations) - img_combinations.combinations.index(img_combination)} pins in product {product.ident}')
    logger.info(f'Pin for product {product.ident} is made.')


def _make_pin_by_template(tasks: schemas.PinTask, all_tags: list[pb_schemas.Tag]):
    """Make pins by template."""
    pb_session = pb_admin.PbSession(SITE_URL, PB_LOGIN, PB_PASSWORD)
    logger.info(f'Making pins by template {tasks.template_name}...')
    for product in tasks.products:
        if tasks.template_name == STANDARD_TEMPLATE_NAME:
            _make_std_template(product, all_tags, pb_session)
        elif tasks.template_name == COLLAGE_TEMPLATE_NAME:
            _make_collage_template(product, all_tags, pb_session)
        logger.info(f'Left {len(tasks.products) - tasks.products.index(product)} products in template {tasks.template_name}')
    logger.info(f'Pins by template {tasks.template_name} are made.')
    logger.info('Ordering new pins...')
    db_tools.order_new_pins()


def refresh_queue():
    """Refresh the queue of pins to be made."""
    pb_session = pb_admin.PbSession(SITE_URL, PB_LOGIN, PB_PASSWORD)
    logger.info('Getting products...')
    products = pb_session.products.get_list()
    logger.info(f'Got {len(products)} products.')
    new_tasks = db_tools.get_new_tasks(products)
    logger.info(f'Got {sum([len(p.products) for p in new_tasks])} new tasks.')
    all_tags = pb_session.tags.get_list()
    for new_task in new_tasks:
        _make_pin_by_template(new_task, all_tags)


if __name__ == '__main__':
    refresh_queue()
