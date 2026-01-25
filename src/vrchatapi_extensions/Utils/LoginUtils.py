import getpass
from multiprocessing import pool
from typing import Tuple, Optional

import vrchatapi
from vrchatapi.api_client import ApiClient
from vrchatapi.exceptions import UnauthorizedException
from vrchatapi.api.authentication_api import AuthenticationApi
from vrchatapi.models.two_factor_auth_code import TwoFactorAuthCode
from vrchatapi.models.two_factor_email_code import TwoFactorEmailCode

from src.vrchatapi_extensions import Data
from src.vrchatapi_extensions import Constant
from src.vrchatapi_extensions.Data import Cookie


def manual_login(
    username: Optional[str] = None,
    password: Optional[str] = None
) -> Tuple[pool.ApplyResult, Optional[Cookie]]:

    """

    :param username:
    :param password:
    :return:
    """

    # Initialize
    config: vrchatapi.Configuration
    client: ApiClient
    auth:   AuthenticationApi
    user:   pool.ApplyResult
    header: Optional[str]
    cookie: Optional[Cookie]

    # Process
    if username is None:
        username = input("Username or Email: ")
    if password is None:
        password = getpass.getpass("Password: ")

    config = vrchatapi.Configuration(
        username=username,
        password=password
    )

    with ApiClient(config) as client:
        client.user_agent = Constant.AGENT
        auth = AuthenticationApi(client)

    try:
        user, _, header = auth.get_current_user_with_http_info()
        cookie = Data.Cookie.extract(header)
        if cookie is not None:
            cookie.save()
    except UnauthorizedException as e:
        auth = __two_factor_auth(auth, e.reason)
        user, _, header = auth.get_current_user_with_http_info()
        cookie = Data.Cookie.extract(header)
        if cookie is None:
            cookie = Data.Cookie.extract(e.headers)
        cookie.save()

    return user, cookie


def cookie_login(
    cookie: Data.Cookie
) -> Tuple[pool.ApplyResult, Optional[Cookie]]:

    """

    :param cookie:
    :return:
    """

    # Initialize
    config: vrchatapi.Configuration
    client: ApiClient
    header: Optional[str]
    auth:   AuthenticationApi
    user:   pool.ApplyResult
    cookie: Optional[Cookie]

    # Process
    config = vrchatapi.Configuration()

    with ApiClient(config) as client:
        client.user_agent = Constant.AGENT

        header = f"auth={cookie.auth}"
        client.default_headers["Cookie"] = header

        auth = AuthenticationApi(client)

    try:
        user = auth.get_current_user()
    except UnauthorizedException:
        user, cookie = manual_login()
        if cookie is not None:
            cookie.save()

    return user, cookie


def __two_factor_auth(
    auth: AuthenticationApi,
    reason: str
) -> AuthenticationApi:

    """

    :param auth:
    :param reason:
    :return:
    """

    # Initialize
    code: str

    # Process
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