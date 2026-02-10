"""Add users.username.

Revision ID: a12b3c4d5e6f
Revises: 5d0d0e6d0d2a
Create Date: 2026-02-10
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a12b3c4d5e6f'
down_revision = '5d0d0e6d0d2a'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('username', sa.String(length=80), nullable=True))
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Populate usernames from email local-parts, ensuring uniqueness.
    bind = op.get_bind()
    users = bind.execute(sa.text("SELECT id, email FROM users ORDER BY id")).fetchall()

    used = set()
    for row in users:
        user_id = row.id
        email = row.email or ''
        base = (email.split('@')[0] if '@' in email else email).strip() or 'user'
        base = ''.join(ch if (ch.isalnum() or ch in ('_', '-')) else '_' for ch in base).strip('_')[:80] or 'user'

        candidate = base
        suffix = 1
        while candidate.lower() in used:
            suffix += 1
            tail = f"_{suffix}"
            candidate = (base[: max(1, 80 - len(tail))] + tail)[:80]

        used.add(candidate.lower())
        bind.execute(sa.text("UPDATE users SET username=:u WHERE id=:id"), {"u": candidate, "id": user_id})


def downgrade():
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_column('users', 'username')

