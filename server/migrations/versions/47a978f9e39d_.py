"""empty message

Revision ID: 47a978f9e39d
Revises: 77b576c21a49
Create Date: 2023-09-04 11:48:58.245241

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '47a978f9e39d'
down_revision = '77b576c21a49'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('investment_view', sa.Column('asset_class', sa.String(length=50), nullable=True))
    op.drop_column('investment_view', 'type')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('investment_view', sa.Column('type', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.drop_column('investment_view', 'asset_class')
    # ### end Alembic commands ###