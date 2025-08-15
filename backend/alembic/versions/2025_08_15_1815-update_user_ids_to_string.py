"""Update user ID columns to String for Firebase compatibility

Revision ID: update_user_ids_to_string
Revises: b504233c1a0d
Create Date: 2025-08-15 18:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "update_user_ids_to_string"
down_revision = "b504233c1a0d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Update user ID columns to String(128) for Firebase UIDs
    with op.batch_alter_table("collections") as batch_op:
        batch_op.alter_column("created_by", type_=sa.String(128))
        batch_op.alter_column("updated_by", type_=sa.String(128))

    with op.batch_alter_table("products") as batch_op:
        batch_op.alter_column("created_by", type_=sa.String(128))
        batch_op.alter_column("updated_by", type_=sa.String(128))

    with op.batch_alter_table("files") as batch_op:
        batch_op.alter_column("created_by", type_=sa.String(128))
        batch_op.alter_column("updated_by", type_=sa.String(128))

    with op.batch_alter_table("product_variants") as batch_op:
        batch_op.alter_column("created_by", type_=sa.String(128))
        batch_op.alter_column("updated_by", type_=sa.String(128))

    with op.batch_alter_table("size_charts") as batch_op:
        batch_op.alter_column("created_by", type_=sa.String(128))
        batch_op.alter_column("updated_by", type_=sa.String(128))

    with op.batch_alter_table("technical_drawings") as batch_op:
        batch_op.alter_column("created_by", type_=sa.String(128))
        batch_op.alter_column("updated_by", type_=sa.String(128))

    with op.batch_alter_table("technical_specifications") as batch_op:
        batch_op.alter_column("created_by", type_=sa.String(128))
        batch_op.alter_column("updated_by", type_=sa.String(128))

    with op.batch_alter_table("product_images") as batch_op:
        batch_op.alter_column("created_by", type_=sa.String(128))
        batch_op.alter_column("updated_by", type_=sa.String(128))


def downgrade() -> None:
    # Convert back to UUID type
    with op.batch_alter_table("collections") as batch_op:
        batch_op.alter_column("created_by", type_=sa.UUID())
        batch_op.alter_column("updated_by", type_=sa.UUID())

    with op.batch_alter_table("products") as batch_op:
        batch_op.alter_column("created_by", type_=sa.UUID())
        batch_op.alter_column("updated_by", type_=sa.UUID())

    with op.batch_alter_table("files") as batch_op:
        batch_op.alter_column("created_by", type_=sa.UUID())
        batch_op.alter_column("updated_by", type_=sa.UUID())

    with op.batch_alter_table("product_variants") as batch_op:
        batch_op.alter_column("created_by", type_=sa.UUID())
        batch_op.alter_column("updated_by", type_=sa.UUID())

    with op.batch_alter_table("size_charts") as batch_op:
        batch_op.alter_column("created_by", type_=sa.UUID())
        batch_op.alter_column("updated_by", type_=sa.UUID())

    with op.batch_alter_table("technical_drawings") as batch_op:
        batch_op.alter_column("created_by", type_=sa.UUID())
        batch_op.alter_column("updated_by", type_=sa.UUID())

    with op.batch_alter_table("technical_specifications") as batch_op:
        batch_op.alter_column("created_by", type_=sa.UUID())
        batch_op.alter_column("updated_by", type_=sa.UUID())

    with op.batch_alter_table("product_images") as batch_op:
        batch_op.alter_column("created_by", type_=sa.UUID())
        batch_op.alter_column("updated_by", type_=sa.UUID())
