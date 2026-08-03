"""remove unused problem starter code

Revision ID: e7f8a9b0c1d2
Revises: d5e6f7a8b9c0
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e7f8a9b0c1d2"
down_revision: Union[str, None] = "d5e6f7a8b9c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("problems", "starter_code_json")


def downgrade() -> None:
    op.add_column(
        "problems",
        sa.Column("starter_code_json", sa.JSON(), nullable=True),
    )
