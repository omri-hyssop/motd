"""Switch MOTD options to weekday-based.

Revision ID: 4c62b7c8a2a4
Revises: 3a4b91df08ef
Create Date: 2026-02-10
"""

from alembic import op
import sqlalchemy as sa


revision = '4c62b7c8a2a4'
down_revision = '3a4b91df08ef'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('motd_options') as batch_op:
        batch_op.add_column(sa.Column('weekday', sa.Integer(), nullable=True))
        batch_op.alter_column('motd_date', existing_type=sa.Date(), nullable=True)

    # Backfill weekday from motd_date where present.
    op.execute("UPDATE motd_options SET weekday = EXTRACT(DOW FROM motd_date)::int - 1 WHERE motd_date IS NOT NULL AND weekday IS NULL")
    # Postgres DOW: Sunday=0 .. Saturday=6. We want Monday=0..Sunday=6.
    # The subtraction above makes Monday=0, Tuesday=1, ... Saturday=5, Sunday=-1.
    op.execute("UPDATE motd_options SET weekday = 6 WHERE weekday = -1")

    # Remove old uniqueness/indexes by date; replace with weekday-based.
    with op.batch_alter_table('motd_options') as batch_op:
        batch_op.drop_constraint('uq_restaurant_motd_date', type_='unique')

    op.drop_index('idx_motd_date_restaurant', table_name='motd_options')

    op.create_index('idx_motd_weekday_restaurant', 'motd_options', ['weekday', 'restaurant_id'])
    op.create_unique_constraint('uq_restaurant_motd_weekday', 'motd_options', ['restaurant_id', 'weekday'])

    # Make weekday non-null now that it's populated.
    with op.batch_alter_table('motd_options') as batch_op:
        batch_op.alter_column('weekday', existing_type=sa.Integer(), nullable=False)


def downgrade():
    with op.batch_alter_table('motd_options') as batch_op:
        batch_op.drop_constraint('uq_restaurant_motd_weekday', type_='unique')

    op.drop_index('idx_motd_weekday_restaurant', table_name='motd_options')

    with op.batch_alter_table('motd_options') as batch_op:
        batch_op.alter_column('motd_date', existing_type=sa.Date(), nullable=False)
        batch_op.drop_column('weekday')

    op.create_index('idx_motd_date_restaurant', 'motd_options', ['motd_date', 'restaurant_id'])
    op.create_unique_constraint('uq_restaurant_motd_date', 'motd_options', ['restaurant_id', 'motd_date'])

