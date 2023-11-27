from typing import Optional
from pydantic import BaseModel, field_validator
from pb_admin import schemas as pb_schemas


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
