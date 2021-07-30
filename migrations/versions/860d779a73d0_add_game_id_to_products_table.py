"""add_game_id_to_products_table

Revision ID: 860d779a73d0
Revises: 
Create Date: 2021-07-27 18:36:26.904454

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '860d779a73d0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('products', sa.Column('game_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'products', 'games', ['game_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'products', type_='foreignkey')
    op.drop_column('products', 'game_id')
    # ### end Alembic commands ###