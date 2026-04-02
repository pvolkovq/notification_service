from datetime import datetime
from urllib.parse import urljoin

import httpx
from sqlalchemy import select

from app.core.config import host_name
from app.core.contants import ERR_MSG, CallOperators
from app.models import Account, Call, Integration
from app.utils.encryptor import decrypt_data


class CallClient:
    def __init__(self, to, code, account_id, options, session):
        self.account = None
        self.integration = None
        self.call = None
        self.to = to
        self.code = code
        self.account_id = account_id
        self.options = options
        self.session = session

    async def process(self):
        if self.account_id:
            result = await self.session.execute(
                select(Account).where(
                    Account.id == self.account_id
                ))
        else:
            result = await self.session.execute(
                select(Account)
                .join(Account.integration)
                .where(Account.is_default == True, Integration.type == Integration.CALL)
            )

        self.account = result.scalar_one_or_none()
        self.account_id = self.account.id
        if self.account:
            self.integration = self.account.integration

        await self.create_call()

    def get_payload_messagio(self):
        return {
            "recipients": [{"phone": self.to}],
            "channels": ["flashcall"],
            "options": {
                "ttl": 60,
                "dlr_callback_url": urljoin(
                    host_name, "/api/v1/retrieve_phone_call_status"
                ),
                "external_id": str(self.call.id),
            },
            "flashcall": {
                "from": "XPANS_flashcall",
                "content": [{"type": "text", "text": self.call.content}],
            },
        }

    def get_headers_messagio(self):
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Messaggio-Login": decrypt_data(self.account.token),
        }

    async def create_call(self):
        self.call = Call(
            content=self.code,
            phone=self.to,
            options=self.options,
            status=Call.PENDING,
            account_id=self.account.id,
        )
        self.session.add(self.call)
        await self.session.commit()
        if self.integration.name == CallProviders.MESSAGIO:
            await self.send_with_messagio()

    async def send_with_messagio(self):
        self.call.status = Call.IN_PROCESS
        await self.session.commit()

        try:
            payload = self.get_payload_messagio()
            headers = self.get_headers_messagio()
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://msg.messaggio.com/api/v1/send",
                    json=payload,
                    headers=headers,
                )

                body = response.json()
                self.call.options = payload

                if response.status_code == 200:
                    self.call.ext_id = body["messages"][0]["message_id"]
                    self.call.ext_status_code = response.status_code

                    if "error" not in body["messages"][0]:
                        self.call.status = Call.COMPLETED
                    else:
                        self.call.status = Call.FAILED
                        self.call.log += ERR_MSG.format(
                            datetime=datetime.now(),
                            func=self.send_with_messagio.__name__,
                            error=str(body),
                        )
                else:
                    self.call.status = Call.FAILED
                    self.call.log = f"{datetime.now()} - send - {response.status_code}"
                    self.call.log += f"\n {body}"

        except Exception as e:
            self.call.status = Call.FAILED
            self.call.log = ERR_MSG.format(
                datetime=datetime.now(), func=self.send_with_messagio.__name__, error=e
            )

        await self.session.commit()
        return self.call.id
