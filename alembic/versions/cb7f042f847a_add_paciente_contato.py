"""add_paciente_contato

Revision ID: cb7f042f847a
Revises: a81f3b3ccdf8
Create Date: 2026-06-29 11:12:43.141095

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb7f042f847a'
down_revision: Union[str, Sequence[str], None] = 'a81f3b3ccdf8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('interconsulta_pedidos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('paciente_contato', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('interconsulta_pedidos', schema=None) as batch_op:
        batch_op.drop_column('paciente_contato')
