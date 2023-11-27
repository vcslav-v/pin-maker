from pin_maker import db_tools, pin_templates, pinterest, schemas, space_tools
from pin_maker.config import (
    COLLAGE_TEMPLATE_NAME,
    PB_LOGIN,
    PB_PASSWORD,
    SITE_URL,
    STANDARD_TEMPLATE_NAME,
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


def _make_std_template(product: pb_schemas.Product, all_tags: list[pb_schemas.Tag]):
    """Make pins by std template."""
    pb_session = pb_admin.PbSession(SITE_URL, PB_LOGIN, PB_PASSWORD)
    full_product = pb_session.products.get(product.ident, product.product_type)
    full_product.description = _remove_html_tags(full_product.description)
    if not full_product.is_live \
            or not full_product.main_image_retina \
            or not full_product.title \
            or not full_product.description \
            or not full_product.slug \
            or not full_product.url:
        return
    img_file = pin_templates.std_pin(full_product)
    img_space_key = space_tools.save_to_space(
        img_file.getvalue(),
        STANDARD_TEMPLATE_NAME,
        f'{product.slug}.jpg'
    )
    img_file.close()
    _tags = [tag for tag in all_tags if tag.ident in full_product.tags_ids]
    pin_description = pinterest.make_description(_tags, full_product.description)
    key_words = ', '.join([tag.name for tag in _tags])
    db_tools.save_pin_task(
        full_product,
        pin_description,
        key_words,
        img_space_key,
        STANDARD_TEMPLATE_NAME
    )


def _make_collage_template(product: pb_schemas.Product, all_tags: list[pb_schemas.Tag]):
    """Make pins by collage template."""
    pb_session = pb_admin.PbSession(SITE_URL, PB_LOGIN, PB_PASSWORD)
    full_product = pb_session.products.get(product.ident, product.product_type)
    full_product.description = _remove_html_tags(full_product.description)
    if not full_product.is_live \
            or not full_product.main_image_retina \
            or not full_product.title \
            or not full_product.description \
            or not full_product.slug \
            or not full_product.url:
        return
    img_combinations = pin_templates.make_combinations_for_glued(full_product)
    _tags = [tag for tag in all_tags if tag.ident in full_product.tags_ids]
    pin_description = pinterest.make_description(_tags, full_product.description)
    key_words = ', '.join([tag.name for tag in _tags])
    for img_combination in img_combinations.combinations:
        img_file = pin_templates.make_glued_pin(img_combination)
        img_space_key = space_tools.save_to_space(
            img_file.getvalue(),
            COLLAGE_TEMPLATE_NAME,
            f'{product.slug}_{uuid.uuid4().hex[:8]}.jpg'
        )
        img_file.close()
        db_tools.save_pin_task(
            full_product,
            pin_description,
            key_words,
            img_space_key,
            COLLAGE_TEMPLATE_NAME
        )


def _make_pin_by_template(tasks: schemas.PinTask, all_tags: list[pb_schemas.Tag]):
    """Make pins by template."""
    for product in tasks.products:
        if tasks.template_name == STANDARD_TEMPLATE_NAME:
            _make_std_template(product, all_tags)
        elif tasks.template_name == COLLAGE_TEMPLATE_NAME:
            _make_collage_template(product, all_tags)
    db_tools.order_new_pins()


def refresh_queue():
    """Refresh the queue of pins to be made."""
    pb_session = pb_admin.PbSession(SITE_URL, PB_LOGIN, PB_PASSWORD)
    products = pb_session.products.get_list()
    new_tasks = db_tools.get_new_tasks(products)
    all_tags = pb_session.tags.get_list()
    for new_task in new_tasks:
        _make_pin_by_template(new_task, all_tags)


if __name__ == '__main__':
    refresh_queue()
