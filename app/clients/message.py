from datetime import datetime
from urllib.parse import urljoin

import httpx
from sqlalchemy import select

from app.core.config import (host_name, messagio_bearer_token,
                             messagio_login_token, messagio_msg_url,
                             messagio_otp_url, smsaero_base_url,
                             telegram_gateway_url)
from app.core.contants import ERR_MSG, MessageChannels, MessageOperators
from app.models import Account, Feature, Integration, Message, MessageTemplate
from app.utils.encryptor import decrypt_data
from app.utils.parser import parse_uri_data
from app.validators.message import validate_data


class MessageClient:
    def __init__(self, text, to, account_id, options, session, key=None):
        self.account = None
        self.integration = None
        self.message = None
        self.parameters = None
        self.headers = None
        self.template_key = key
        self.text = text
        self.to = validate_data(to)
        self.account_id = account_id
        self.host_name = host_name
        self.options = options
        self.session = session
        self.channel = MessageChannels.WHATSAPP

    async def process(self):
        if self.account_id:
            result = await self.session.execute(
                select(Account).where(Account.id == self.account_id)
            )
        elif "operator" in self.options:
            operator = self.options["operator"]
            if operator in MessageOperators.ALL:
                result = await self.session.execute(
                    select(Account)
                    .join(Account.integration)
                    .where(
                        Integration.name == operator,
                        Integration.type == Integration.MESSAGE,
                    )
                )
        else:
            result = await self.session.execute(
                select(Account)
                .join(Account.integration)
                .where(
                    Account.is_default == True, Integration.type == Integration.MESSAGE
                )
            )

        self.account = result.scalar_one_or_none()
        if self.account:
            self.integration = self.account.integration

        if self.template_key:
            self.text = await self.parse_template()

        self.get_parameters()
        result = await self.create_message()
        return result

    async def parse_template(self):
        result = await self.session.execute(
            select(MessageTemplate).where(MessageTemplate.type == self.template_key)
        )
        template = result.scalar_one_or_none()
        if template:
            return template.content.replace("%v", self.text)
        else:
            return self.text

    def get_parameters(self):
        if self.integration.name == MessageOperators.TELEGRAM:
            self.headers = {
                "Authorization": f"Bearer {decrypt_data(self.account.token)}",
                "Content-Type": "application/json",
            }
        if self.integration.name == MessageOperators.SMSAERO:
            account_data, account_options = parse_uri_data(
                decrypt_data(self.account.uri)
            )
            self.parameters = {
                "email": account_data.username,
                "api_key": account_data.password,
                "sign": account_options["SIGN"],
                "shortLink": self.options.get("shortLink", None),
                "callbackUrl": urljoin(self.host_name, "/api/v1/retrieve_sms_status"),
            }
        if self.integration.name == MessageOperators.SMSRU:
            account_data, account_options = parse_uri_data(
                decrypt_data(self.account.uri)
            )
            self.parameters = {
                "api_id": account_options["API_ID"],
                "to": self.to,
                "msg": self.text,
                "from": account_options["SIGN"],
                "json": 1,
            }
        if self.integration.name == MessageOperators.MESSAGIO:
            if self.options and "channels" in self.options:
                # для совместимости, один хрен в channels прилетает только один канал
                self.channel = self.options["channels"][0]

            if self.channel in MessageChannels.ALL:
                if self.channel == MessageChannels.WHATSAPP:
                    self.headers = {
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                        "Messaggio-Login": messagio_login_token,
                    }
                if self.channel == MessageChannels.TELEGRAM:
                    self.headers = {
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {messagio_bearer_token}",
                    }
                    self.parameters = {
                        "to": self.to,
                        "channel": MessageChannels.TELEGRAM,
                        "code": self.text,
                    }
                if self.channel == MessageChannels.SMS:
                    self.headers = {
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {messagio_bearer_token}",
                    }
                    self.parameters = {
                        "to": self.to,
                        "channel": MessageChannels.SMS,
                        "code": self.text,
                    }

    async def create_message(self):
        self.message = Message(
            content=self.text,
            phone=self.to,
            options=self.options,
            status=Message.PENDING,
            account_id=self.account.id,
        )
        self.session.add(self.message)
        await self.session.commit()
        result = False
        if self.integration.name == MessageOperators.SMSAERO:
            result = await self.send_with_smsaero()
        elif self.integration.name == MessageOperators.SMSRU:
            result = await self.send_with_smsru()
        elif self.integration.name == MessageOperators.MESSAGIO:
            result = await self.send_with_messagio()
        elif self.integration.name == MessageOperators.TELEGRAM:
            result = await self.send_with_telegram()

        return result

    async def send_with_telegram(self):
        payload = {
            "phone_number": self.message.phone,
            "code": self.text,
            "ttl": 60,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                urljoin(telegram_gateway_url, "sendVerificationMessage"),
                json=payload,
                headers=self.headers,
                timeout=10,
            )
            result = response.json()
            if response.status_code == 200 and result["ok"]:
                self.message.status = Feature.COMPLETED
                self.message.log = str(result)
                self.message.ext_id = result["result"]["request_id"]
                self.message.ext_status_code = response.status_code
            else:
                self.message.status = Feature.FAILED
                self.message.log = str(result)
                self.message.ext_status_code = response.status_code

        await self.session.commit()
        return self.message

    async def send_with_messagio(self):
        result = None
        try:
            if self.channel == MessageChannels.WHATSAPP:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        messagio_msg_url,
                        json=self.payload_messagio(),
                        headers=self.headers,
                        timeout=10,
                    )
                    result = response.json()
                    self.message.status = Feature.COMPLETED
                    self.message.ext_id = result["messages"][0]["message_id"]
                    self.message.ext_status_code = response.status_code

            if self.channel == MessageChannels.TELEGRAM:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        messagio_otp_url,
                        json=self.parameters,
                        headers=self.headers,
                        timeout=10,
                    )
                    if response.status_code == 202:
                        result = response.json()
                        self.message.status = Feature.COMPLETED
                        self.message.ext_id = result["auth_id"]
                        self.message.ext_status_code = response.status_code
                    else:
                        self.message.log = response.text
                        self.message.status = Message.FAILED

            if self.channel == MessageChannels.SMS:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        messagio_otp_url,
                        json=self.parameters,
                        headers=self.headers,
                        timeout=10,
                    )
                    if response.status_code == 202:
                        result = response.json()
                        self.message.status = Feature.COMPLETED
                        self.message.ext_id = result["auth_id"]
                        self.message.ext_status_code = response.status_code
                    else:
                        self.message.log = response.text
                        self.message.status = Message.FAILED
        except Exception as e:
            self.message.log = ERR_MSG.format(
                datetime=datetime.now(), func=self.send_with_messagio.__name__, error=e
            )
        if not result:
            self.message.status = Message.FAILED

        await self.session.commit()
        return self.message

    async def send_with_smsaero(self):
        try:
            params = {
                "number": self.to,
                "text": self.text,
                "sign": self.parameters.get("sign", ""),
                "shortLink": self.parameters.get("shortLink", 0),
                "callbackUrl": self.parameters.get("callbackUrl", ""),
            }
            auth = (self.parameters["email"], self.parameters["api_key"])
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    smsaero_base_url, params=params, auth=auth, timeout=30
                )
                result = response.json()
                data = result.get("data", {})
                self.message.ext_id = str(data.get("id", ""))
                self.message.ext_status_code = response.status_code

                status = data.get("status")
                success = result.get("success", False)
                if status in [0, 1]:
                    self.message.status = Message.COMPLETED
                    self.message.log = str(result)
                elif status in [2, 6]:
                    self.message.status = Message.FAILED
                    self.message.log = str(result)
                elif not success:
                    self.message.status = Message.FAILED
                    self.message.log = str(result)
        except Exception as e:
            self.message.status = Message.FAILED
            self.message.log = e
        await self.session.commit()
        return self.message

    async def send_with_smsru(self):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    smsaero_base_url, params=self.parameters, timeout=30
                )
            if response.status_code == 200:
                body = response.json()
                if "sms" in response:
                    response_data = body.get("sms")[self.to]
                    self.message.log = f"{response.text}"
                    self.message.ext_id = response_data.get("sms_id")
                    self.message.ext_status_code = response.status_code
                    if self.message.ext_status_code == 100:
                        self.message.status = Message.COMPLETED
                    else:
                        self.message.status = Message.FAILED
                        self.message.log = str(body)
            else:
                self.message.status = Message.FAILED
        except Exception as e:
            self.message.status = Message.FAILED
            self.message.log = e
        await self.session.commit()
        return self.message

    def payload_messagio(self):
        return {
            "recipients": [{"phone": self.message.phone}],
            "channels": [self.channel],
            "options": {
                "ttl": 60,
                # "dlr_callback_url": "https://example.com/dlr",
                # "external_id": "messaggio-acc-external-id-0"
                "external_id": str(self.message.id),
            },
            "whatsapp": {
                "from": "XpansDataSlWA",
                "content": [
                    {
                        "type": "template",
                        "template": {
                            "language": "en",
                            "id": "xpans_otp",
                            "body": {"parameters": [{"text": self.text}]},
                            "buttons": [{"type": "url", "url_parameter": self.text}],
                        },
                    }
                ],
            },
            "sms": {
                "from": "XpansDataSl",
                "content": [{"type": "text", "text": self.message.content}],
            },
        }
