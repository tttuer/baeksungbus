"""Add attachments to answers.

Revision ID: 20260901_0004
Revises: 20260622_0003
Create Date: 2026-09-01
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = "20260901_0004"
down_revision: Union[str, Sequence[str], None] = "20260622_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("answer", sa.Column("attachment", mysql.LONGBLOB(), nullable=True))
    op.add_column("answer", sa.Column("attachment_filename", mysql.VARCHAR(length=1024), nullable=True))


def downgrade() -> None:
    op.drop_column("answer", "attachment_filename")
    op.drop_column("answer", "attachment")
