"""add_user_sessions_table

Revision ID: a1b2c3d4e5f6
Revises: 9b92792938cd
Create Date: 2026-09-21 20:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '9b92792938cd'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = inspector.get_table_names()
    if 'user_sessions' not in tables:
        op.create_table(
            'user_sessions',
            sa.Column('id', sa.String(length=64), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('role', sa.String(length=20), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('last_activity', sa.DateTime(), nullable=False),
            sa.Column('is_active', sa.Boolean(), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_user_sessions_user_id', 'user_sessions', ['user_id'], unique=False)
        op.create_index('ix_user_sessions_is_active', 'user_sessions', ['is_active'], unique=False)


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = inspector.get_table_names()
    if 'user_sessions' in tables:
        op.drop_index('ix_user_sessions_is_active', table_name='user_sessions')
        op.drop_index('ix_user_sessions_user_id', table_name='user_sessions')
        op.drop_table('user_sessions')
