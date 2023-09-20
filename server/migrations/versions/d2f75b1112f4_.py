"""empty message

Revision ID: d2f75b1112f4
Revises: 292a27f1d7dc
Create Date: 2023-09-19 11:45:00.062469

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2f75b1112f4'
down_revision = '292a27f1d7dc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('customer', sa.Column('subscription_start_date', sa.DateTime(), nullable=True))
    op.add_column('customer', sa.Column('is_premium', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('customer', 'is_premium')
    op.drop_column('customer', 'subscription_start_date')
    # ### end Alembic commands ###