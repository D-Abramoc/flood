from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict
from app.database import get_async_session
from app.crud.messages import message_crud
from app.schemas.messages import MessageRead, MessageCreate
from app.crud.users import user_crud
from app.dependencies import get_current_user
from app.models import User
import asyncio

router = APIRouter(prefix='/chat', tags=['Chat'])
templates = Jinja2Templates(directory='app/templates')


@router.get('/', response_class=HTMLResponse, summary='Chat Page')
async def get_chat_page(
    request: Request,
    user_data: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Сераница чата."""
    users_all = await user_crud.find_all(session=session)
    return templates.TemplateResponse(
        'chat.html',
        {
            'request': request,
            'user': user_data,
            'users_all': users_all
        }
    )


@router.get('/messages/{user_id}', response_model=List[MessageRead])
async def get_messages(
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    return await message_crud.get_messages_between_users(
        user_id_1=user_id,
        user_id_2=current_user.id,
        session=session
    ) or []


# Активные WebSocket-подключения: {user_id: websocket}
active_connections: Dict[int, WebSocket] = {}


async def notify_user(user_id: int, message: dict):
    '''Отправить сообщение пользователю, если он подключен.'''
    if user_id in active_connections:
        websocket = active_connections[user_id]
        await websocket.send_json(message)


@router.websocket('/ws/{user_id}')
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """WebSocket эндпоинт для соединений."""
    await websocket.accept()
    active_connections[user_id] = websocket
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        active_connections.pop(user_id, None)


@router.post('/messages', response_model=MessageCreate)
async def send_message(
    message: MessageCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    await message_crud.add(
        session=session,
        sender_id=current_user.id,
        content=message.content,
        recipient_id=message.recipient_id
    )
    message_data = {
        'sender_id': current_user.id,
        'recipient_id': message.recipient_id,
        'content': message.content,
    }
    await notify_user(message.recipient_id, message_data)
    await notify_user(current_user.id, message_data)
    return {
        'recipient_id': message.recipient_id,
        'content': message.content,
        'status': 'ok',
        'msg': 'Message saved!'
    }
