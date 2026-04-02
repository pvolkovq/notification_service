import smtplib
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from sqlalchemy import select

from app.core.contants import ERR_MSG
from app.models import Account, Email, Integration
from app.models.mail import EmailFiles
from app.utils.encryptor import decrypt_data
from app.utils.parser import parse_uri_data
from app.validators.message import validate_data


class EmailClient:
    def __init__(self, subject, content, to, files, account_id, options, session):
        self.account = None
        self.integration = None
        self.email = None
        self.email_file = None
        self.subject = validate_data(subject)
        self.content = validate_data(content)
        self.account_id = account_id
        self.to = validate_data(to)
        self.files = files
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
                .where(
                    Account.is_default == True, Integration.type == Integration.EMAIL
                )
            )
        self.account = result.scalar_one_or_none()
        if self.account:
            self.integration = self.account.integration
            self.account_id = self.account.id
        await self.create_email()

    async def create_email(self):
        self.email = Email(
            email=self.to.lower(),
            content=self.content,
            subject=self.subject,
            account_id=self.account_id,
            options=self.options,
            status=Email.PENDING,
        )
        self.session.add(self.email)
        await self.session.commit()
        await self.send()

    def _create_message(self):
        print(decrypt_data(self.account.uri))
        account_data, account_options = parse_uri_data(decrypt_data(self.account.uri))
        message = MIMEMultipart("alternative")
        message["From"] = account_data.username
        message["To"] = self.to
        message["Subject"] = self.subject
        if "<html>" in self.content:
            text_part = MIMEText(self.content, "html")
        else:
            text_part = MIMEText(self.content, "plain")
        message.attach(text_part)
        if self.files:
            for file_data in self.files:
                if file_data:
                    resp = requests.get(file_data["url"])
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(resp.content)
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename={file_data['name']}",
                    )
                    message.attach(part)
                    self.email_file = EmailFiles(
                        email_id=self.email.id, title=file_data["name"], url=file_data["url"]
                    )
                    self.email_file.save(self.session)
        return message.as_string()

    async def send(self):
        msg = self._create_message()
        account_data, account_options = parse_uri_data(decrypt_data(self.account.uri))
        try:
            server = smtplib.SMTP(host=account_data.hostname, port=account_data.port)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(account_data.username, account_data.password)
            server.sendmail(from_addr=account_data.username, to_addrs=self.to, msg=msg)
            server.quit()
        except Exception as e:
            self.email.status = Email.FAILED
            self.email.log = ERR_MSG.format(
                datetime=datetime.now(), func=self.send.__name__, error=e
            )
        else:
            self.email.status = Email.COMPLETED
        await self.session.commit()
        return self.email.id
