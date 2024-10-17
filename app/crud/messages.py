from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Message


class CRUDMessage(CRUDBase):

    async def get_messages_between_users(
            self,
            user_id_1: int,
            user_id_2: int,
            session: AsyncSession
    ):
        stmt = select(self.model).filter(
            or_(
                and_(
                    self.model.sender_id == user_id_1,
                    self.model.recipient_id == user_id_2
                    ),
                and_(
                    self.model.sender_id == user_id_2,
                    self.model.recipient_id == user_id_1
                    )
            )
        ).order_by(self.model.id)
        result = await session.execute(stmt)
        return result.scalars().all()


message_crud = CRUDMessage(Message)
