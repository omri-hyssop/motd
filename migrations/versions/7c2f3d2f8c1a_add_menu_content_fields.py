"""Add menu content fields.

Revision ID: 7c2f3d2f8c1a
Revises: bb2dac9a2c82
Create Date: 2026-02-09
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7c2f3d2f8c1a'
down_revision = 'bb2dac9a2c82'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('menus') as batch_op:
        batch_op.add_column(sa.Column('menu_text', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('menu_file_path', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('menu_file_mime', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('menu_file_name', sa.String(length=255), nullable=True))


def downgrade():
    with op.batch_alter_table('menus') as batch_op:
        batch_op.drop_column('menu_file_name')
        batch_op.drop_column('menu_file_mime')
        batch_op.drop_column('menu_file_path')
        batch_op.drop_column('menu_text')

