"""Add users.birth_date.

Revision ID: 5d0d0e6d0d2a
Revises: 4c62b7c8a2a4
Create Date: 2026-02-10
"""

from alembic import op
import sqlalchemy as sa


revision = '5d0d0e6d0d2a'
down_revision = '4c62b7c8a2a4'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('birth_date', sa.Date(), nullable=True))


def downgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('birth_date')

