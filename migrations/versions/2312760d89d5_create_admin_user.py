"""create admin user

Revision ID: 2312760d89d5
Revises: 3fed3f10a974
Create Date: 2025-11-20 15:15:59.782770

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import uuid
from datetime import datetime, timezone
from passlib.context import CryptContext


# revision identifiers, used by Alembic.
revision: str = '2312760d89d5'
down_revision: Union[str, Sequence[str], None] = '3fed3f10a974'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


    conn = op.get_bind()

    admin_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    admin_email = "admin@gmail.com"
    admin_name = "Administrador"
    admin_password = pwd_context.hash("Senha@123")


    conn.execute(
        sa.text(
            """
            INSERT INTO "user" 
                (id, name, email, password, permissions, created_at, updated_at, flg_deleted)
            VALUES 
                (:id, :name, :email, :password, :permissions, :created_at, :updated_at, :flg_deleted)
            ON CONFLICT (email) DO NOTHING
            """
        ),
        {
            "id": str(admin_id),          
            "name": admin_name,
            "email": admin_email,
            "password": admin_password,
            "permissions": ["admin"],     
            "created_at": now,
            "updated_at": now,
            "flg_deleted": False,
        },
    )



def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            DELETE FROM "user"
            WHERE email = :email
            """
        ),
        {"email": "admin@gmail.com"},
    )