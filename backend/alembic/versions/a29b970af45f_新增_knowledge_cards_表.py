"""新增 knowledge_cards 表

Revision ID: a29b970af45f
Revises: 17fc4b05d0cc
Create Date: 2026-06-02 16:39:20.518974

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a29b970af45f'
down_revision: Union[str, Sequence[str], None] = '17fc4b05d0cc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('knowledge_cards',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('source', sa.String(length=200), nullable=True),
    sa.Column('tags', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('knowledge_cards', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_knowledge_cards_user_id'), ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('knowledge_cards', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_knowledge_cards_user_id'))

    op.drop_table('knowledge_cards')
