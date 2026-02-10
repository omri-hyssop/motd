"""Add order_text and restaurant availability support.

Revision ID: 1f2d0e9d9a4c
Revises: 9e0e6c1af2a1
Create Date: 2026-02-09
"""

from alembic import op
import sqlalchemy as sa


revision = '1f2d0e9d9a4c'
down_revision = '9e0e6c1af2a1'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('orders') as batch_op:
        batch_op.add_column(sa.Column('order_text', sa.Text(), nullable=True))


def downgrade():
    with op.batch_alter_table('orders') as batch_op:
        batch_op.drop_column('order_text')

