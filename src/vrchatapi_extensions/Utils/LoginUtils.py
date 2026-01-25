from vrchatapi.api_client import ApiClient
from vrchatapi.api.authentication_api import AuthenticationApi
from vrchatapi.models.two_factor_auth_code import TwoFactorAuthCode
from vrchatapi.models.two_factor_email_code import TwoFactorEmailCode

from .. import Data
from .. import Constant


def __setup_manual_client(client: ApiClient) -> ApiClient:
    return client


def __setup_cookie_client(client: ApiClient, cookie: Data.Cookie) -> ApiClient:

    """

    :param client:
    :param cookie:
    :return:
    """

    client.user_agent = Constant.AGENT
    cookie_header = f"auth={cookie.auth}"
    if cookie.two_factor_auth is not None:
        cookie_header += f"; twoFactorAuth={cookie.two_factor_auth}"
    client.default_headers["Cookie"] = cookie_header

    return client


def __two_factor_auth(auth: AuthenticationApi, reason: str) -> AuthenticationApi:

    """

    :param auth:
    :param reason:
    :return:
    """

    if "Email 2 Factor Authentication" in reason:
        code = input("Email 2FA Code: ")
        auth.verify2_fa_email_code(
            two_factor_email_code=TwoFactorEmailCode(code)
        )
    elif "2 Factor Authentication" in reason:
        code = input("2FA Code: ")
        auth.verify2_fa(
            two_factor_auth_code=TwoFactorAuthCode(code)
        )

    return auth