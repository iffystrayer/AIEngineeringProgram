"""Add encryption support for session data (NFR-5.1)

Revision ID: 05_add_encryption_support
Revises: 04_add_users_table
Create Date: 2025-10-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '05_add_encryption_support'
down_revision = '04_add_users_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add encryption support columns."""
    # Add encrypted flag to stage_data
    op.add_column('stage_data', sa.Column('encrypted', sa.Boolean(), nullable=False, server_default='false'))

    # Add encrypted_value column to store encrypted data
    op.add_column('stage_data', sa.Column('encrypted_value', sa.Text(), nullable=True))

    # Add encrypted flag to conversation_history
    op.add_column('conversation_history', sa.Column('encrypted', sa.Boolean(), nullable=False, server_default='false'))

    # Add indexes for encrypted flag queries
    op.create_index('idx_stage_data_encrypted', 'stage_data', ['encrypted'], unique=False)
    op.create_index('idx_conversation_encrypted', 'conversation_history', ['encrypted'], unique=False)


def downgrade() -> None:
    """Remove encryption support."""
    # Drop indexes
    op.drop_index('idx_conversation_encrypted', table_name='conversation_history')
    op.drop_index('idx_stage_data_encrypted', table_name='stage_data')

    # Drop columns
    op.drop_column('conversation_history', 'encrypted')
    op.drop_column('stage_data', 'encrypted_value')
    op.drop_column('stage_data', 'encrypted')
