"""create game table

Revision ID: 539823ed7cd0
Revises:
Create Date: 2025-07-26 15:01:27.015717

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "539823ed7cd0"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        DROP FUNCTION IF EXISTS update_updated_at_column;
    """
    )
