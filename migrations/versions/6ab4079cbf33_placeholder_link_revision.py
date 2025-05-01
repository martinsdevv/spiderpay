"""placeholder link revision

Revision ID: 6ab4079cbf33
Revises: e2cc5f014d80
Create Date: 2025-05-01 15:18:40.704329

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ab4079cbf33'
down_revision: Union[str, None] = 'e2cc5f014d80'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
