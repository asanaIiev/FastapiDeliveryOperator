from hmac import compare_digest

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from config import settings


class AdminAuthentication(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get('username')
        password = form.get('password')

        if not settings.ADMIN_USERNAME or not settings.ADMIN_PASSWORD:
            return False
        if not isinstance(username, str) or not isinstance(password, str):
            return False

        valid_username = compare_digest(username, settings.ADMIN_USERNAME)
        valid_password = compare_digest(password, settings.ADMIN_PASSWORD)
        if not (valid_username and valid_password):
            return False

        request.session['admin_authenticated'] = True
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return request.session.get('admin_authenticated') is True
