"""settings.value طولانی‌تر برای متن‌های قابل ویرایش

Revision ID: 0003
Revises: 0002
"""
from alembic import op
import sqlalchemy as sa

revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('settings') as b:
        b.alter_column('value', existing_type=sa.String(length=200), type_=sa.String(length=400), existing_nullable=False)


def downgrade() -> None:
    with op.batch_alter_table('settings') as b:
        b.alter_column('value', existing_type=sa.String(length=400), type_=sa.String(length=200), existing_nullable=False)
