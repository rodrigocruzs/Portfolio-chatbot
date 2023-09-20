"""empty message

Revision ID: 7b9c0631b714
Revises: 47b525c0d3b3
Create Date: 2023-09-17 13:53:31.702418

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b9c0631b714'
down_revision = '47b525c0d3b3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_question',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('question', sa.String(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['customer.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_question_id'), 'user_question', ['id'], unique=False)
    op.create_index(op.f('ix_user_question_question'), 'user_question', ['question'], unique=False)
    op.create_index(op.f('ix_user_question_user_id'), 'user_question', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_question_user_id'), table_name='user_question')
    op.drop_index(op.f('ix_user_question_question'), table_name='user_question')
    op.drop_index(op.f('ix_user_question_id'), table_name='user_question')
    op.drop_table('user_question')
    # ### end Alembic commands ###