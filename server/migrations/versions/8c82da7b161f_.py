"""empty message

Revision ID: 8c82da7b161f
Revises: 64cf265779b1
Create Date: 2023-08-23 17:16:24.251791

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c82da7b161f'
down_revision = '64cf265779b1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('investment_holding', sa.Column('unofficial_currency_code', sa.String(length=10), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('investment_holding', 'unofficial_currency_code')
    # ### end Alembic commands ###
