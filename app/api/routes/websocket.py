import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

from app.db.database import AsyncSessionLocal
from app.db.repositories.service import ServiceRepository
from app.core.security import get_current_user


router = APIRouter()


@router.websocket("/ws/status")
async def websocket_status(
    websocket: WebSocket,
    current_user: str = Depends(get_current_user)
) -> None:
    await websocket.accept()

    try:
        while True:
            async with AsyncSessionLocal() as session:
                repository = ServiceRepository(session)

                services = await repository.get_all()

                data = [
                    {
                        "id": service.id,
                        "name": service.name,
                        "state": service.state.value,
                    }
                    for service in services
                ]

            await websocket.send_json(data)

            await asyncio.sleep(5)

    except WebSocketDisconnect:
        pass