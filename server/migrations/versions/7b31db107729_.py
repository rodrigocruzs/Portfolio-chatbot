"""empty message

Revision ID: 7b31db107729
Revises: bf795a489842
Create Date: 2023-08-22 17:56:14.123591

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b31db107729'
down_revision = 'bf795a489842'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('investment_transaction', sa.Column('investment_transaction_id', sa.String(length=255), nullable=False))
    op.drop_column('investment_transaction', 'transaction_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('investment_transaction', sa.Column('transaction_id', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
    op.drop_column('investment_transaction', 'investment_transaction_id')
    # ### end Alembic commands ###
