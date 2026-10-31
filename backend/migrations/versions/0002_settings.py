"""settings table

Revision ID: 0002
Revises: 0001
"""
from alembic import op
import sqlalchemy as sa

revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'settings',
        sa.Column('key', sa.String(length=50), primary_key=True),
        sa.Column('value', sa.String(length=200), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('settings')
