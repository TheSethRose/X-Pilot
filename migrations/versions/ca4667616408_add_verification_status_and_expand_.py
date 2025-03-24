"""Add verification status and expand tweet text column

Revision ID: ca4667616408
Revises: 35375fd0ed75
Create Date: 2025-03-24 03:53:07.139931

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ca4667616408'
down_revision = '35375fd0ed75'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tweets', schema=None) as batch_op:
        batch_op.alter_column('text',
               existing_type=sa.VARCHAR(length=280),
               type_=sa.Text(),
               existing_nullable=False)

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_verified', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('verified_type', sa.String(length=64), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('verified_type')
        batch_op.drop_column('is_verified')

    with op.batch_alter_table('tweets', schema=None) as batch_op:
        batch_op.alter_column('text',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(length=280),
               existing_nullable=False)

    # ### end Alembic commands ###
