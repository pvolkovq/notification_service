from urllib.parse import urljoin

import httpx
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.clients.message import MessageClient
from app.core.config import (
    messagio_bearer_token,
    messagio_otp_check_status_url,
    telegram_gateway_token,
    telegram_gateway_url,
)
from app.core.contants import MessageChannels, MessageDeliveryStatus, MessageOperators
from app.core.database import get_session
from app.schemes.message import MessageRequest, MessageStatus

router = APIRouter()


@router.post("/api/v1/send_sms/", status_code=status.HTTP_202_ACCEPTED)
async def send_sms(
    item: MessageRequest,
    session: AsyncSession = Depends(get_session),
):
    client = MessageClient(
        key=item.key,
        text=item.text,
        to=item.to,
        account_id=item.account_id,
        options=item.options,
        session=session,
    )
    result = await client.process()
    return {"ok": True, "result": result}


@router.post("/api/v1/check_status/", status_code=status.HTTP_200_OK)
async def check_status(
    item: MessageStatus,
    session: AsyncSession = Depends(get_session),
):
    data = {}
    if item.operator == MessageOperators.MESSAGIO and item.channel in [
        MessageChannels.TELEGRAM,
        MessageChannels.SMS,
    ]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                messagio_otp_check_status_url,
                json={"auth_ids": [item.code]},
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {messagio_bearer_token}",
                },
                timeout=10,
            )
            result = response.json()
            codes = result.get("codes")
            data["code"] = item.code
            for code in codes:
                for report in code["delivery_reports"]:
                    if report["status"] == "SEND_SUCCESS":
                        data["status"] = MessageDeliveryStatus.SUCCESS
                        data["channel"] = report["channel"]
                    if report["status"] == "SEND_FAIL":
                        data["status"] = MessageDeliveryStatus.FAILED
                        data["channel"] = report["channel"]
                    if report["status"] == "SEND_FATAL":
                        data["status"] = MessageDeliveryStatus.FAILED
                        data["channel"] = report["channel"]
    if item.operator == MessageOperators.TELEGRAM:
        payload = {
            "request_id": item.code,
        }
        headers = {
            "Authorization": f"Bearer {telegram_gateway_token}",
            "Content-Type": "application/json",
        }
        data["channel"] = "telegram"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                urljoin(telegram_gateway_url, "checkVerificationStatus"),
                json=payload,
                headers=headers,
                timeout=10,
            )
            result = response.json()
            delivery_status = result["result"]["delivery_status"]["status"]
            if delivery_status == "delivered":
                data["status"] = MessageDeliveryStatus.SUCCESS
            if delivery_status == "read":
                data["status"] = MessageDeliveryStatus.SUCCESS
            if delivery_status == "sent":
                data["status"] = MessageDeliveryStatus.PENDING
            if delivery_status == "expired":
                data["status"] = MessageDeliveryStatus.FAILED
            if delivery_status == "revoked":
                data["status"] = MessageDeliveryStatus.FAILED
    # if item.operator == MessageOperators.SMSAERO:
    #     async with httpx.AsyncClient() as client:
    #         response = await client.post(
    #             smsaero_check_status_url,
    #             json={},
    #             headers={
    #                 "Accept": "application/json",
    #                 "Content-Type": "application/json",
    #             },
    #             timeout=10,
    #         )
    #         result = response.json()
    if data:
        return {"ok": True, "result": data}
    return {"ok": False, "result": None}
