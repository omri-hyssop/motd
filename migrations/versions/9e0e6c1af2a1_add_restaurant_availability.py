"""Add restaurant availability table.

Revision ID: 9e0e6c1af2a1
Revises: 7c2f3d2f8c1a
Create Date: 2026-02-09
"""

from alembic import op
import sqlalchemy as sa


revision = '9e0e6c1af2a1'
down_revision = '7c2f3d2f8c1a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'restaurant_availability',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('restaurant_id', sa.Integer(), sa.ForeignKey('restaurants.id'), nullable=False),
        sa.Column('weekday', sa.Integer(), nullable=False),
        sa.Column('is_available', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('restaurant_id', 'weekday', name='uq_restaurant_weekday'),
    )
    op.create_index('idx_weekday_available', 'restaurant_availability', ['weekday', 'is_available'])
    op.create_index(op.f('ix_restaurant_availability_restaurant_id'), 'restaurant_availability', ['restaurant_id'])


def downgrade():
    op.drop_index(op.f('ix_restaurant_availability_restaurant_id'), table_name='restaurant_availability')
    op.drop_index('idx_weekday_available', table_name='restaurant_availability')
    op.drop_table('restaurant_availability')

