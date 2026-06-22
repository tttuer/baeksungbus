"""Create initial application tables.

Revision ID: 20260619_0001
Revises:
Create Date: 2026-06-19
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = "20260619_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "bus_schedule",
        sa.Column("route_number", sa.String(length=255), nullable=False),
        sa.Column("url", mysql.LONGTEXT(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("images", mysql.LONGTEXT(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
    )
    op.create_table(
        "ddock",
        sa.Column("image", mysql.LONGBLOB(), nullable=True),
        sa.Column("image_name", mysql.VARCHAR(length=1024), nullable=True),
        sa.Column("order", sa.Integer(), nullable=False, quote=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
    )
    op.create_table(
        "notice",
        sa.Column("writer", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("title", mysql.LONGTEXT(), nullable=False),
        sa.Column("content", mysql.LONGTEXT(), nullable=True),
        sa.Column("attachment", mysql.LONGBLOB(), nullable=True),
        sa.Column("attachment_filename", mysql.VARCHAR(length=1024), nullable=True),
        sa.Column("c_date", sa.String(length=255), nullable=True),
        sa.Column("done", sa.Boolean(), nullable=False),
        sa.Column("read_cnt", sa.Integer(), nullable=False),
        sa.Column(
            "notice_type",
            sa.Enum("TIME", "TTOCK", "NOTICE", name="noticetype"),
            nullable=False,
        ),
        sa.Column("creator", sa.String(length=255), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
    )
    op.create_table(
        "qa",
        sa.Column("writer", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("title", mysql.LONGTEXT(), nullable=False),
        sa.Column("content", mysql.LONGTEXT(), nullable=True),
        sa.Column("attachment", mysql.LONGBLOB(), nullable=True),
        sa.Column("attachment_filename", mysql.VARCHAR(length=1024), nullable=True),
        sa.Column("c_date", sa.String(length=255), nullable=True),
        sa.Column("done", sa.Boolean(), nullable=False),
        sa.Column("read_cnt", sa.Integer(), nullable=False),
        sa.Column("hidden", sa.Boolean(), nullable=False),
        sa.Column(
            "qa_type",
            sa.Enum("CUSTOMER", "LOST", name="qatype"),
            nullable=False,
        ),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
    )
    op.create_table(
        "recruit",
        sa.Column("title", mysql.LONGTEXT(), nullable=False),
        sa.Column("department", mysql.LONGTEXT(), nullable=False),
        sa.Column("note", mysql.LONGTEXT(), nullable=True),
        sa.Column("show", sa.Boolean(), nullable=False, quote=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
    )
    op.create_table(
        "user",
        sa.Column("id", sa.String(length=255), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
    )
    op.create_table(
        "answer",
        sa.Column("content", mysql.LONGTEXT(), nullable=False),
        sa.Column("qa_id", sa.Integer(), nullable=False),
        sa.Column("creator", sa.String(length=255), nullable=True),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(["qa_id"], ["qa.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
    )
    op.create_table(
        "recruit_experience",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("recruit_id", sa.Integer(), nullable=False),
        sa.Column("label", mysql.LONGTEXT(), nullable=False),
        sa.Column("value", mysql.LONGTEXT(), nullable=False),
        sa.ForeignKeyConstraint(["recruit_id"], ["recruit.id"]),
        sa.PrimaryKeyConstraint("id"),
        if_not_exists=True,
    )


def downgrade() -> None:
    op.drop_table("recruit_experience")
    op.drop_table("answer")
    op.drop_table("user")
    op.drop_table("recruit")
    op.drop_table("qa")
    op.drop_table("notice")
    op.drop_table("ddock")
    op.drop_table("bus_schedule")
