"""Add MOTD options table.

Revision ID: 3a4b91df08ef
Revises: 2b1d6c7b9c31
Create Date: 2026-02-10
"""

from alembic import op
import sqlalchemy as sa


revision = '3a4b91df08ef'
down_revision = '2b1d6c7b9c31'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'motd_options',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('restaurant_id', sa.Integer(), sa.ForeignKey('restaurants.id'), nullable=False),
        sa.Column('motd_date', sa.Date(), nullable=False),
        sa.Column('option_text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('restaurant_id', 'motd_date', name='uq_restaurant_motd_date'),
    )
    op.create_index('idx_motd_date_restaurant', 'motd_options', ['motd_date', 'restaurant_id'])
    op.create_index(op.f('ix_motd_options_motd_date'), 'motd_options', ['motd_date'])
    op.create_index(op.f('ix_motd_options_restaurant_id'), 'motd_options', ['restaurant_id'])


def downgrade():
    op.drop_index(op.f('ix_motd_options_restaurant_id'), table_name='motd_options')
    op.drop_index(op.f('ix_motd_options_motd_date'), table_name='motd_options')
    op.drop_index('idx_motd_date_restaurant', table_name='motd_options')
    op.drop_table('motd_options')

