from fastapi import FastAPI, Depends
from sqladmin import Admin

from app.admin.admin import (AccountAdmin, CallAdmin, EmailAdmin,
                             EmailFilesAdmin, IntegrationAdmin, MessageAdmin,
                             MessageTemplateAdmin, PushAdmin)
from app.admin.auth import authentication_backend
from app.api import call, mail, message, npd, push
from app.core.config import debug
from app.core.database import sessionmanager
from app.auth import verify_token

app = FastAPI()
sessionmanager.init_db()

admin = Admin(
    app,
    engine=sessionmanager.engine,
    session_maker=sessionmanager.session_factory,
    base_url="/admin",
    title="Notification Service Admin",
    favicon_url="https://uploader.ma.direct/get?id=01K9EXEM9ZPDNBJEE76WQVQC5X",
    middlewares=None,
    debug=debug,
    authentication_backend=authentication_backend,
)

app.include_router(npd.router, dependencies=[Depends(verify_token)])
app.include_router(call.router, dependencies=[Depends(verify_token)])
app.include_router(mail.router, dependencies=[Depends(verify_token)])
app.include_router(message.router, dependencies=[Depends(verify_token)])
app.include_router(push.router, dependencies=[Depends(verify_token)])

admin.add_view(AccountAdmin)
admin.add_view(IntegrationAdmin)
admin.add_view(MessageAdmin)
admin.add_view(MessageTemplateAdmin)
admin.add_view(EmailAdmin)
admin.add_view(EmailFilesAdmin)
admin.add_view(PushAdmin)
admin.add_view(CallAdmin)
