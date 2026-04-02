import json
from datetime import datetime
from urllib.parse import urljoin

import google.auth.transport.requests
import httpx
from google.oauth2 import service_account
from sqlalchemy import select

from app.core.config import google_fcm_base_url, realms_map, scopes
from app.core.contants import ERR_MSG
from app.models import Account, Integration, Push
from app.utils.encryptor import decrypt_data


class PushClient:
    def __init__(self, token, text, account_id, options, session):
        self.account = None
        self.integration = None
        self.push = None
        self.token = token
        self.text = text
        self.account_id = account_id
        self.options = options
        self.session = session

    async def process(self):
        if self.account_id:
            result = await self.session.execute(
                select(Account).where(
                    Account.id == self.account_id
                ))
        elif "realm" in self.options and self.options["realm"]:
            result = await self.session.execute(
                select(Account)
                .join(Account.integration)
                .where(
                    Account.realm == self.options["realm"],
                    Integration.type == Integration.PUSH,
                )
            )
        else:
            result = await self.session.execute(
                select(Account)
                .join(Account.integration)
                .where(Account.is_default == True, Integration.type == Integration.PUSH)
            )

        self.account = result.scalar_one_or_none()
        self.account_id = self.account.id
        if self.account:
            self.integration = self.account.integration

        await self.create_push()
        return self.push.id

    def _get_fcm_url(self):
        project_id = realms_map[self.options["realm"]]
        fcm_endpoint = f"v1/projects/{project_id}/messages:send"
        return urljoin(google_fcm_base_url, fcm_endpoint)

    def _get_access_token(self):
        # print(decrypt_data(self.account.custom_fields))
        google_config = json.loads(decrypt_data(self.account.custom_fields)).get(
            "config"
        )
        credentials = service_account.Credentials.from_service_account_info(
            google_config, scopes=scopes
        )

        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        return credentials.token

    async def create_push(self):
        self.push = Push(
            content=self.text,
            push_token=self.token,
            options=self.options,
            status=Push.PENDING,
            account_id=self.account_id,
        )
        self.session.add(self.push)
        await self.session.commit()

        try:
            headers = {
                "Authorization": f"Bearer {self._get_access_token()}",
                "Content-Type": "application/json; UTF-8",
            }
            message = {
                "message": {
                    "token": self.token,
                    "android": {"direct_boot_ok": True, "priority": "high"},
                    "apns": {
                        "payload": {"aps": {"badge": 1}},
                        "headers": {
                            "apns-priority": "10",
                            "content_available": "true",
                        },
                    },
                    "notification": {"title": "Mlnagents", "body": self.text},
                    "data": {"title": "Mlnagents", "message": self.text},
                }
            }
            if self.options and self.options.get("entity_type"):
                message["message"]["data"]["entity_type"] = self.options.get(
                    "entity_type"
                )
            fcm_url = self._get_fcm_url()
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    fcm_url,
                    data=json.dumps(message),
                    headers=headers,
                )
                if response.status_code == 200:
                    self.push.status = Push.COMPLETED
                    self.push.log = response.text
                else:
                    self.push.status = Push.FAILED
                    self.push.log = response.text
        except Exception as e:
            self.push.status = Push.FAILED
            self.push.log = str(e)
        await self.session.commit()
