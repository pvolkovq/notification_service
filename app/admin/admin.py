from typing import Any

from sqladmin import ModelView
from wtforms import SelectField

from app.models.account import Account
from app.models.call import Call
from app.models.integration import Integration
from app.models.mail import Email, EmailFiles
from app.models.message import Message
from app.models.message_template import MessageTemplate
from app.models.push import Push
from app.utils.encryptor import encrypt_data


class EmailAdmin(ModelView, model=Email):
    column_list = [Email.id, Email.email, Email.subject, Email.status, Email.created_at]
    column_details_exclude_list = [Email.log]
    column_searchable_list = [Email.email, Email.subject]
    column_sortable_list = [Email.id, Email.created_at, Email.status]
    column_default_sort = [(Email.created_at, True)]
    name = "Email"
    name_plural = "Emails"


class EmailFilesAdmin(ModelView, model=EmailFiles):
    column_list = [EmailFiles.id, EmailFiles.title, EmailFiles.url]
    column_searchable_list = [EmailFiles.title]
    name = "Email File"
    name_plural = "Email Files"


class MessageAdmin(ModelView, model=Message):
    column_list = [
        Message.id,
        Message.account,
        Message.phone,
        Message.content,
        Message.status,
        Message.created_at,
    ]
    column_details_exclude_list = [Message.log]
    column_searchable_list = [Message.phone, Message.content]
    column_sortable_list = [Message.id, Message.created_at, Message.status]
    column_default_sort = [(Message.created_at, True)]
    name = "Messages"
    name_plural = "SMS Messages"


class PushAdmin(ModelView, model=Push):

    column_list = [Push.id, Push.content, Push.status, Push.created_at]
    column_details_exclude_list = [Push.log]
    column_searchable_list = [Push.content]
    column_sortable_list = [Push.id, Push.created_at, Push.status]
    column_default_sort = [(Push.created_at, True)]
    name = "Push"
    name_plural = "Push Notifications"


class CallAdmin(ModelView, model=Call):
    column_list = [
        Call.id,
        Call.phone,
        Call.content,
        Call.status,
        Call.created_at,
    ]
    column_details_exclude_list = [Call.log]
    column_searchable_list = [Call.phone, Call.content]
    column_sortable_list = [Call.id, Call.created_at, Call.status]
    column_default_sort = [(Call.created_at, True)]
    name = "Call"
    name_plural = "Calls"


class MessageTemplateAdmin(ModelView, model=MessageTemplate):
    column_default_sort = ("id", True)
    column_list = [MessageTemplate.id, MessageTemplate.type, MessageTemplate.content]
    column_searchable_list = [MessageTemplate.type, MessageTemplate.content]
    column_sortable_list = [MessageTemplate.id, MessageTemplate.type]
    name = "Message Template"
    name_plural = "Message Templates"


class AccountAdmin(ModelView, model=Account):
    column_default_sort = ("id", True)
    column_list = [
        Account.id,
        Account.name,
        Account.realm,
        Account.integration,
        Account.is_default,
    ]
    column_sortable_list = [
        Account.id,
        Account.name,
        Account.realm,
        Account.integration,
        Account.is_default,
    ]
    form_excluded_columns = [Account.message, Account.call, Account.push, Account.email]
    column_details_exclude_list = [
        Account.message,
        Account.call,
        Account.push,
        Account.email,
    ]
    name = "Account"
    name_plural = "Accounts"

    async def on_model_change(
        self, data: dict[str, Any], model: Account, is_created: bool, request
    ) -> None:
        password = data.get("password")
        uri = data.get("uri")
        certificate = data.get("certificate")
        custom_fields = data.get("custom_fields")
        token = data.get("token")
        if password:
            data["password"] = encrypt_data(password)
        if uri:
            data["uri"] = encrypt_data(uri)
        if certificate:
            data["certificate"] = encrypt_data(certificate)
        if custom_fields:
            data["custom_fields"] = encrypt_data(custom_fields)
        if token:
            data["token"] = encrypt_data(token)


class IntegrationAdmin(ModelView, model=Integration):
    column_default_sort = ("id", True)
    column_list = [Integration.id, Integration.name, Integration.type]
    column_searchable_list = [Integration.id, Integration.name, Integration.type]
    column_sortable_list = [Integration.id, Integration.name, Integration.type]
    form_columns = [
        Integration.id,
        Integration.name,
        Integration.description,
        Integration.type,
    ]
    form_overrides = {"type": SelectField}
    form_args = {
        "type": {
            "choices": [
                (Integration.MESSAGE, Integration.MESSAGE),
                (Integration.PUSH, Integration.PUSH),
                (Integration.CALL, Integration.CALL),
                (Integration.EMAIL, Integration.EMAIL),
                (Integration.ANOTHER, Integration.ANOTHER),
            ],
            "coerce": str,
        }
    }
    name = "Integration"
    name_plural = "Integrations"
