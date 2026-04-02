from fastapi import APIRouter
from starlette import status

from app.clients.npd import NpdClient
from app.schemes.npd import InnRequest, NotificationsRequest

router = APIRouter()


@router.post("/api/v1/npd/notifications/", status_code=status.HTTP_200_OK)
async def get_notifications(request: InnRequest):
    data = NpdClient().get_notifications({"inn": request.inn})
    return data["data"]


@router.post("/api/v1/npd/notifications_count/", status_code=status.HTTP_200_OK)
async def get_notifications_count(request: InnRequest):
    data = NpdClient().get_notifications_count({"inn": request.inn})
    return data["data"]


@router.post("/api/v1/npd/notifications_delivered/", status_code=status.HTTP_200_OK)
async def notifications_delivered(request: NotificationsRequest):
    data = NpdClient().set_notifications_delivered(
        {"inn": request.inn, "notifications": request.notifications}
    )
    return data["data"]


@router.post("/api/v1/npd/notifications_readed/", status_code=status.HTTP_200_OK)
async def notifications_readed(request: NotificationsRequest):
    data = NpdClient().set_notifications_readed(
        {"inn": request.inn, "notifications": request.notifications}
    )
    return data["data"]
