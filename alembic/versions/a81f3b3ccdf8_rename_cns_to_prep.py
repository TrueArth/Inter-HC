"""rename cns to prep

Revision ID: a81f3b3ccdf8
Revises: eccfa4ee91c7
Create Date: 2026-06-26 19:42:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a81f3b3ccdf8'
down_revision: Union[str, Sequence[str], None] = 'eccfa4ee91c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename column using batch operations for SQLite compatibility
    with op.batch_alter_table('interconsulta_pedidos', schema=None) as batch_op:
        batch_op.alter_column('paciente_cns', new_column_name='paciente_prep')
        batch_op.drop_index('ix_interconsulta_pedidos_paciente_cns')
        batch_op.create_index(batch_op.f('ix_interconsulta_pedidos_paciente_prep'), ['paciente_prep'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('interconsulta_pedidos', schema=None) as batch_op:
        batch_op.alter_column('paciente_prep', new_column_name='paciente_cns')
        batch_op.drop_index(batch_op.f('ix_interconsulta_pedidos_paciente_prep'))
        batch_op.create_index('ix_interconsulta_pedidos_paciente_cns', ['paciente_cns'], unique=False)
