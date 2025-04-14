"""second commit

Revision ID: c73e4ba04ed6
Revises: b14f516db61b
Create Date: 2024-11-06 12:10:17.536966

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c73e4ba04ed6'
down_revision: Union[str, None] = 'b14f516db61b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
