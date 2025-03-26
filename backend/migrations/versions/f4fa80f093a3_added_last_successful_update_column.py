"""Added last_successful_update column

Revision ID: f4fa80f093a3
Revises: 73684eb0c72b
Create Date: 2025-03-24 17:35:10.121864

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'f4fa80f093a3'
down_revision: Union[str, None] = '73684eb0c72b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('plaidaccount', sa.Column('last_successful_update', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('plaidaccount', 'last_successful_update')
    # ### end Alembic commands ###
