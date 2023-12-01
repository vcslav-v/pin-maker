"""empty message

Revision ID: e8b8a83bd98c
Revises: cbb92e185770
Create Date: 2023-11-28 08:56:43.158244

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8b8a83bd98c'
down_revision: Union[str, None] = 'cbb92e185770'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('no_format_products',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('product_type', sa.String(), nullable=False),
    sa.Column('template_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['template_id'], ['templates.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('no_format_products')
    # ### end Alembic commands ###