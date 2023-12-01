from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from typing import Optional


class Base(DeclarativeBase):
    pass


class Info(Base):
    '''Info.'''

    __tablename__ = 'info'

    id: Mapped[int] = mapped_column(primary_key=True)
    pinterest_cookies: Mapped[Optional[str]] = mapped_column(nullable=True)


class Pin(Base):
    '''Pin.'''

    __tablename__ = 'pins'

    id: Mapped[int] = mapped_column(primary_key=True)
    order: Mapped[Optional[int]] = mapped_column(nullable=True)
    product_id: Mapped[int] = mapped_column()
    product_type: Mapped[str] = mapped_column()
    product_url: Mapped[str] = mapped_column()
    on_main_board: Mapped[bool] = mapped_column(default=False)
    on_special_board: Mapped[Optional[bool]] = mapped_column(default=False, nullable=True)
    title: Mapped[Optional[str]] = mapped_column(nullable=True)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    media_do_key: Mapped[Optional[str]] = mapped_column(nullable=True)
    key_words: Mapped[Optional[str]] = mapped_column(nullable=True)

    template_id: Mapped[int] = mapped_column(ForeignKey('templates.id'))
    template: Mapped['Template'] = relationship('Template', back_populates='pins')


class Template(Base):
    '''Template.'''

    __tablename__ = 'templates'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    pin_limit_per_day: Mapped[int] = mapped_column(default=300)

    pins: Mapped[list['Pin']] = relationship(back_populates='template')

    no_format_products: Mapped[list['NoFormatProduct']] = relationship(back_populates='template')


class NoFormatProduct(Base):
    '''NoFormatProduct.'''

    __tablename__ = 'no_format_products'

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column()
    product_type: Mapped[str] = mapped_column()

    template_id: Mapped[int] = mapped_column(ForeignKey('templates.id'))
    template: Mapped['Template'] = relationship('Template', back_populates='no_format_products')