import uuid

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.core.config import admin_password, auth_secret_key


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]
        if form["username"] == "admin" and password == admin_password:
            request.session.update({"token": str(uuid.uuid4())})
            return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        return True


authentication_backend = AdminAuth(secret_key=auth_secret_key)
