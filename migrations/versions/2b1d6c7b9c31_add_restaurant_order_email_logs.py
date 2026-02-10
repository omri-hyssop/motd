"""Add restaurant order email log table.

Revision ID: 2b1d6c7b9c31
Revises: 1f2d0e9d9a4c
Create Date: 2026-02-10
"""

from alembic import op
import sqlalchemy as sa


revision = '2b1d6c7b9c31'
down_revision = '1f2d0e9d9a4c'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'restaurant_order_email_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('restaurant_id', sa.Integer(), sa.ForeignKey('restaurants.id'), nullable=False),
        sa.Column('order_date', sa.Date(), nullable=False),
        sa.Column('sent_by_user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('restaurant_id', 'order_date', name='uq_restaurant_order_email_date'),
    )
    op.create_index('idx_email_logs_date_restaurant', 'restaurant_order_email_logs', ['order_date', 'restaurant_id'])
    op.create_index(op.f('ix_restaurant_order_email_logs_order_date'), 'restaurant_order_email_logs', ['order_date'])
    op.create_index(op.f('ix_restaurant_order_email_logs_restaurant_id'), 'restaurant_order_email_logs', ['restaurant_id'])


def downgrade():
    op.drop_index(op.f('ix_restaurant_order_email_logs_restaurant_id'), table_name='restaurant_order_email_logs')
    op.drop_index(op.f('ix_restaurant_order_email_logs_order_date'), table_name='restaurant_order_email_logs')
    op.drop_index('idx_email_logs_date_restaurant', table_name='restaurant_order_email_logs')
    op.drop_table('restaurant_order_email_logs')

