"""Add item and sub item

Revision ID: 23580c5fc67e
Revises: 77dc08b8493f
Create Date: 2020-08-10 08:23:31.139463

"""
from alembic import op  # noqa: E402
import sqlalchemy as sa  # noqa: E402
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "23580c5fc67e"
down_revision = "77dc08b8493f"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "item",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=True),
        sa.Column("expiry", sa.DateTime(), nullable=True),
        sa.Column("flake_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("openfoodfacts_product", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "sub_item",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=True),
        sa.Column("expiry", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["item_id"], ["item.id"],),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("sub_item")
    op.drop_table("item")
    # ### end Alembic commands ###