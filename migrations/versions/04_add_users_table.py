"""Add users table for authentication

Revision ID: 04_add_users_table
Revises: 03033cebb647
Create Date: 2025-10-24 20:30:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "04_add_users_table"
down_revision = "03033cebb647"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create users table for authentication."""
    # Create users table matching sessions.user_id type (VARCHAR)
    op.create_table(
        "users",
        sa.Column("user_id", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.TIMESTAMP(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("user_id"),
    )

    # Create indexes for performance
    op.create_index("idx_users_email", "users", ["email"], unique=True)
    op.create_index("idx_users_created_at", "users", [sa.text("created_at DESC")])

    # Note: sessions table already has user_id column from init.sql
    # Skip creating FK for now due to existing sessions data
    # Will be addressed in next migration if needed


def downgrade() -> None:
    """Drop users table and related indexes."""
    # Drop indexes
    op.drop_index("idx_users_created_at", table_name="users")
    op.drop_index("idx_users_email", table_name="users")

    # Drop table
    op.drop_table("users")
