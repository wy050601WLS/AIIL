"""Message 表新增 images 字段

Revision ID: 17fc4b05d0cc
Revises: ab691b1384ad
Create Date: 2026-06-02 16:29:59.997406

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '17fc4b05d0cc'
down_revision: Union[str, Sequence[str], None] = 'ab691b1384ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.add_column(sa.Column('images', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('messages', schema=None) as batch_op:
        batch_op.drop_column('images')
