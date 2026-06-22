"""Expand user-facing text columns.

Revision ID: 20260622_0003
Revises: 20260622_0002
Create Date: 2026-06-22
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = "20260622_0003"
down_revision: Union[str, Sequence[str], None] = "20260622_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "ddock",
        "image_name",
        existing_type=sa.String(length=255),
        type_=mysql.VARCHAR(length=1024),
        existing_nullable=True,
    )
    op.alter_column(
        "notice",
        "title",
        existing_type=sa.String(length=255),
        type_=mysql.LONGTEXT(),
        existing_nullable=False,
    )
    op.alter_column(
        "notice",
        "attachment_filename",
        existing_type=sa.String(length=255),
        type_=mysql.VARCHAR(length=1024),
        existing_nullable=True,
    )
    op.alter_column(
        "qa",
        "title",
        existing_type=sa.String(length=255),
        type_=mysql.LONGTEXT(),
        existing_nullable=False,
    )
    op.alter_column(
        "qa",
        "attachment_filename",
        existing_type=sa.String(length=255),
        type_=mysql.VARCHAR(length=1024),
        existing_nullable=True,
    )
    op.alter_column(
        "recruit",
        "title",
        existing_type=sa.String(length=255),
        type_=mysql.LONGTEXT(),
        existing_nullable=False,
    )
    op.alter_column(
        "recruit",
        "department",
        existing_type=sa.String(length=255),
        type_=mysql.LONGTEXT(),
        existing_nullable=False,
    )
    op.alter_column(
        "recruit_experience",
        "label",
        existing_type=sa.String(length=255),
        type_=mysql.LONGTEXT(),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "recruit_experience",
        "label",
        existing_type=mysql.LONGTEXT(),
        type_=sa.String(length=255),
        existing_nullable=False,
    )
    op.alter_column(
        "recruit",
        "department",
        existing_type=mysql.LONGTEXT(),
        type_=sa.String(length=255),
        existing_nullable=False,
    )
    op.alter_column(
        "recruit",
        "title",
        existing_type=mysql.LONGTEXT(),
        type_=sa.String(length=255),
        existing_nullable=False,
    )
    op.alter_column(
        "qa",
        "attachment_filename",
        existing_type=mysql.VARCHAR(length=1024),
        type_=sa.String(length=255),
        existing_nullable=True,
    )
    op.alter_column(
        "qa",
        "title",
        existing_type=mysql.LONGTEXT(),
        type_=sa.String(length=255),
        existing_nullable=False,
    )
    op.alter_column(
        "notice",
        "attachment_filename",
        existing_type=mysql.VARCHAR(length=1024),
        type_=sa.String(length=255),
        existing_nullable=True,
    )
    op.alter_column(
        "notice",
        "title",
        existing_type=mysql.LONGTEXT(),
        type_=sa.String(length=255),
        existing_nullable=False,
    )
    op.alter_column(
        "ddock",
        "image_name",
        existing_type=mysql.VARCHAR(length=1024),
        type_=sa.String(length=255),
        existing_nullable=True,
    )
