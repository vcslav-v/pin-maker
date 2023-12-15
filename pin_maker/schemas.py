from typing import Optional
from pydantic import BaseModel, field_validator
from pb_admin import schemas as pb_schemas
from datetime import datetime


class ImgCombination(BaseModel):
    img_urls: list[str]


class ImgCombinations(BaseModel):
    combinations: list[ImgCombination]


class Pin(BaseModel):
    img_url: Optional[str] = None
    combinations: Optional[list[str]] = None
    title: str
    description: str
    link: Optional[str]

    @field_validator('title', 'description')
    @classmethod
    def to_ascii(cls, row_string: str):
        if row_string.isascii():
            return row_string
        new_sting = []
        for char in row_string:
            if char.isascii():
                new_sting.append(char)
                continue
            if char == '—':
                new_sting.append('-')
        return ''.join(new_sting)


class PinList(BaseModel):
    pins: list[Pin]


class MovePin(BaseModel):
    img_urls: list[str]
    title: str
    description: str

    @field_validator('title', 'description')
    @classmethod
    def to_ascii(cls, row_string: str):
        if row_string.isascii():
            return row_string
        new_sting = []
        for char in row_string:
            if char.isascii():
                new_sting.append(char)
                continue
            if char == '—':
                new_sting.append('-')
        return ''.join(new_sting)


class ProductLink(BaseModel):
    link: str


class Category(BaseModel):
    name: str
    url: str


class Compatibility(BaseModel):
    """Pydantic's model for the compatibility."""
    name: str
    url: str


class ProductInfo(BaseModel):
    pr_type: str
    url: str
    title: str
    thumbnail_url: str
    thumbnail_url_x2: str
    main_img_url: str
    main_img_url_x2: str
    gallery_urls: list[str]
    gallery_retina_urls: list[str]
    exerpt: str
    description: str
    regular_price: Optional[float]
    sale_regular_price: Optional[float]
    categories: list[Category]
    extended_price: Optional[float]
    sale_extended_price: Optional[float]
    compatibilities: list[Compatibility] = []
    formats: list[str]


class PinTask(BaseModel):
    """Pydantic's model for the pin task."""
    template_name: str
    products: list[pb_schemas.Product]


class PinRow(BaseModel):
    """Pydantic's model for the pin row."""
    db_ident: int
    title: str
    media_url: Optional[str] = None
    media_key: str
    board: str
    description: str
    link: str
    key_words: str


class LinkCreate(BaseModel):
    '''LinkCreate.'''

    target_url: str
    source: int | str
    medium: int | str
    campaign_project: int | str
    campaning_dop: str = '0'
    content: int | str = '0'
    term_material: int | str
    term_page: int | str
    user: int | str


class Link(BaseModel):
    '''Link.'''

    id: int
    target_url: str
    campaign_date: datetime
    campaign_dop: str
    full_url: str
    term_material_id: int
    term_material_name: str
    term_page_id: int
    term_page_name: str
    medium_id: int
    medium_name: str
    source_id: int
    source_name: str
    campaign_project_id: int
    campaign_project_name: str
    content_id: int
    content_name: str
    user_id: int
    user_name: str
