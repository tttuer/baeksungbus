"""Expand large content and binary columns.

Revision ID: 20260622_0002
Revises: 20260619_0001
Create Date: 2026-06-22
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = "20260622_0002"
down_revision: Union[str, Sequence[str], None] = "20260619_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "bus_schedule",
        "url",
        existing_type=sa.String(length=255),
        type_=mysql.LONGTEXT(),
        existing_nullable=False,
    )
    op.alter_column(
        "bus_schedule",
        "images",
        existing_type=sa.String(length=255),
        type_=mysql.LONGTEXT(),
        existing_nullable=True,
    )
    op.alter_column(
        "ddock",
        "image",
        existing_type=mysql.BLOB(),
        type_=mysql.LONGBLOB(),
        existing_nullable=True,
    )
    op.alter_column(
        "notice",
        "content",
        existing_type=sa.String(length=255),
        type_=mysql.LONGTEXT(),
        existing_nullable=True,
    )
    op.alter_column(
        "notice",
        "attachment",
        existing_type=mysql.BLOB(),
        type_=mysql.LONGBLOB(),
        existing_nullable=True,
    )
    op.alter_column(
        "qa",
        "content",
        existing_type=sa.String(length=255),
        type_=mysql.LONGTEXT(),
        existing_nullable=True,
    )
    op.alter_column(
        "qa",
        "attachment",
        existing_type=mysql.BLOB(),
        type_=mysql.LONGBLOB(),
        existing_nullable=True,
    )
    op.alter_column(
        "recruit",
        "note",
        existing_type=sa.String(length=255),
        type_=mysql.LONGTEXT(),
        existing_nullable=True,
    )
    op.alter_column(
        "answer",
        "content",
        existing_type=sa.String(length=255),
        type_=mysql.LONGTEXT(),
        existing_nullable=False,
    )
    op.alter_column(
        "recruit_experience",
        "value",
        existing_type=sa.String(length=255),
        type_=mysql.LONGTEXT(),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "recruit_experience",
        "value",
        existing_type=mysql.LONGTEXT(),
        type_=sa.String(length=255),
        existing_nullable=False,
    )
    op.alter_column(
        "answer",
        "content",
        existing_type=mysql.LONGTEXT(),
        type_=sa.String(length=255),
        existing_nullable=False,
    )
    op.alter_column(
        "recruit",
        "note",
        existing_type=mysql.LONGTEXT(),
        type_=sa.String(length=255),
        existing_nullable=True,
    )
    op.alter_column(
        "qa",
        "attachment",
        existing_type=mysql.LONGBLOB(),
        type_=mysql.BLOB(),
        existing_nullable=True,
    )
    op.alter_column(
        "qa",
        "content",
        existing_type=mysql.LONGTEXT(),
        type_=sa.String(length=255),
        existing_nullable=True,
    )
    op.alter_column(
        "notice",
        "attachment",
        existing_type=mysql.LONGBLOB(),
        type_=mysql.BLOB(),
        existing_nullable=True,
    )
    op.alter_column(
        "notice",
        "content",
        existing_type=mysql.LONGTEXT(),
        type_=sa.String(length=255),
        existing_nullable=True,
    )
    op.alter_column(
        "ddock",
        "image",
        existing_type=mysql.LONGBLOB(),
        type_=mysql.BLOB(),
        existing_nullable=True,
    )
    op.alter_column(
        "bus_schedule",
        "images",
        existing_type=mysql.LONGTEXT(),
        type_=sa.String(length=255),
        existing_nullable=True,
    )
    op.alter_column(
        "bus_schedule",
        "url",
        existing_type=mysql.LONGTEXT(),
        type_=sa.String(length=255),
        existing_nullable=False,
    )
