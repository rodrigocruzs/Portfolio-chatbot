"""empty message

Revision ID: 7b4cd4f99401
Revises: c0af797cbf0e
Create Date: 2023-08-23 15:30:20.930904

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b4cd4f99401'
down_revision = 'c0af797cbf0e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'investment_security', ['security_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'investment_security', type_='unique')
    # ### end Alembic commands ###