"""empty message

Revision ID: 26276ed5484e
Revises: c8854d0ad249
Create Date: 2022-07-09 01:54:48.067162

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '26276ed5484e'
down_revision = 'c8854d0ad249'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ecommerce_platforms',
    sa.Column('platform_id', sa.Integer(), nullable=False),
    sa.Column('platform_name', sa.String(length=100), nullable=False),
    sa.Column('platform_slug', sa.String(length=100), nullable=False),
    sa.Column('platform_desc', sa.Text(), nullable=True),
    sa.Column('date_created', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('platform_id'),
    sa.UniqueConstraint('platform_name'),
    sa.UniqueConstraint('platform_slug')
    )
    op.create_table('ecommerce_products',
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('product_name', sa.String(length=100), nullable=False),
    sa.Column('product_slug', sa.String(length=100), nullable=False),
    sa.Column('product_desc', sa.Text(), nullable=True),
    sa.Column('product_platform', sa.Text(), nullable=True),
    sa.Column('date_created', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('product_id'),
    sa.UniqueConstraint('product_name'),
    sa.UniqueConstraint('product_slug')
    )
    op.drop_table('E_commerce_products')
    op.drop_table('E_commerce_platforms')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('E_commerce_platforms',
    sa.Column('platform_id', sa.INTEGER(), nullable=False),
    sa.Column('platform_name', sa.VARCHAR(length=100), nullable=False),
    sa.Column('platform_slug', sa.VARCHAR(length=100), nullable=False),
    sa.Column('platform_desc', sa.TEXT(), nullable=True),
    sa.Column('date_created', sa.DATETIME(), nullable=False),
    sa.PrimaryKeyConstraint('platform_id'),
    sa.UniqueConstraint('platform_name'),
    sa.UniqueConstraint('platform_slug')
    )
    op.create_table('E_commerce_products',
    sa.Column('product_id', sa.INTEGER(), nullable=False),
    sa.Column('product_name', sa.VARCHAR(length=100), nullable=False),
    sa.Column('product_slug', sa.VARCHAR(length=100), nullable=False),
    sa.Column('product_desc', sa.TEXT(), nullable=True),
    sa.Column('product_platform', sa.TEXT(), nullable=True),
    sa.Column('date_created', sa.DATETIME(), nullable=False),
    sa.PrimaryKeyConstraint('product_id'),
    sa.UniqueConstraint('product_name'),
    sa.UniqueConstraint('product_slug')
    )
    op.drop_table('ecommerce_products')
    op.drop_table('ecommerce_platforms')
    # ### end Alembic commands ###
