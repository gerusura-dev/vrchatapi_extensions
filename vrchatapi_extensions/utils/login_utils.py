"""
This module provides functionalities for logging into the VRChat API. It includes
support for manual login, cookie-based login, and handling two-factor authentication.
The module ensures user credentials and authentication processes are properly managed,
with options for secure user input.

The primary functionalities of the module include:
- Manual login with username/password and optional two-factor authentication handling.
- Cookie-based login to reuse existing authentication sessions.
"""


import getpass
from multiprocessing import pool
from typing import Tuple, Optional

import vrchatapi
from vrchatapi.api_client import ApiClient
from vrchatapi.exceptions import UnauthorizedException
from vrchatapi.api.authentication_api import AuthenticationApi
from vrchatapi.models.two_factor_auth_code import TwoFactorAuthCode
from vrchatapi.models.two_factor_email_code import TwoFactorEmailCode

from vrchatapi_extensions.data import Cookie
from vrchatapi_extensions.constant import constant


def manual_login(
    username: Optional[str] = None,
    password: Optional[str] = None,
    agent: Optional[str] = None
) -> Tuple[pool.ApplyResult, Optional[Cookie]]:

    """
    Performs a manual login to the VRChat API and optionally saves a session cookie.
    If no username or password is provided, the function prompts the user to manually
    enter the credentials. If two-factor authentication is required, the appropriate
    procedure is performed automatically.

    :param username: The username or email address of the VRChat account. Optional;
        if not provided, the function will prompt for input (default is None).
    :param password: The password of the VRChat account. Optional; if not provided,
        the function will prompt for input (default is None).
    :param agent: The user agent string to identify the client. Optional;
        defaults to the value defined in Constant.AGENT if not provided.
    :return: A tuple consisting of the user information result and an optional
        session cookie. If authentication fails, the cookie will be None.
    :rtype: Tuple[pool.ApplyResult, Optional[Cookie]]
    :raises UnauthorizedException: If the username and password authentication fails
        or two-factor authentication is not successfully completed.
    """

    # Initialize
    config: vrchatapi.Configuration
    client: ApiClient
    auth:   AuthenticationApi
    user:   pool.ApplyResult
    header: Optional[str]
    cookie: Optional[Cookie]

    # Process
    agent = agent or constant.AGENT

    if username is None:
        username = input("Username or Email: ")
    if password is None:
        password = getpass.getpass("Password: ")

    config = vrchatapi.Configuration(
        username=username,
        password=password
    )

    with ApiClient(config) as client:
        client.user_agent = agent
        auth = AuthenticationApi(client)

    try:
        user, _, header = auth.get_current_user_with_http_info()
        cookie = Cookie.extract(header)
        if cookie is not None:
            cookie.save()
    except UnauthorizedException as e:
        auth = __two_factor_auth(auth, e.reason)
        user, _, header = auth.get_current_user_with_http_info()
        cookie = Cookie.extract(header)
        if cookie is None:
            cookie = Cookie.extract(e.headers)
        cookie.save()

    return user, cookie


def cookie_login(
    cookie: Cookie,
    agent: Optional[str] = None
) -> Tuple[pool.ApplyResult, Optional[Cookie]]:

    """
    Logs into a system using a given cookie and optionally an agent string. This
    function initializes the client configuration, sets up the user agent, and
    performs authentication using the supplied cookie. If the cookie is invalid,
    it attempts a manual login and saves the new cookie if successfully retrieved.

    :param cookie: Authentication cookie containing necessary credentials.
    :type cookie: Cookie
    :param agent: Optional user agent string. Defaults to a pre-defined constant.
    :type agent: Optional[str]
    :return: A tuple containing the user object wrapped in a `pool.ApplyResult`
        and optionally the updated authentication cookie.
    :rtype: Tuple[pool.ApplyResult, Optional[Cookie]]
    """

    # Initialize
    config: vrchatapi.Configuration
    client: ApiClient
    header: Optional[str]
    auth:   AuthenticationApi
    user:   pool.ApplyResult
    cookie: Optional[Cookie]

    # Process
    agent = agent or constant.AGENT

    config = vrchatapi.Configuration()

    with ApiClient(config) as client:
        client.user_agent = agent

        header = f"auth={cookie.auth}"
        client.default_headers["Cookie"] = header

        auth = AuthenticationApi(client)

    try:
        user = auth.get_current_user()
    except UnauthorizedException:
        user, cookie = manual_login(agent=agent)
        if cookie is not None:
            cookie.save()

    return user, cookie


def __two_factor_auth(
    auth: AuthenticationApi,
    reason: str
) -> AuthenticationApi:

    """
    Handles two-factor authentication based on the provided reason and initializes
    the verification process with input codes from the user.

    :param auth: A reference to the AuthenticationApi instance used for verifying
        two-factor authentication codes.
    :type auth: AuthenticationApi
    :param reason: Description of the reason triggering two-factor authentication.
        This determines the type of authentication that should be processed.
    :type reason: str
    :return: The updated AuthenticationApi instance after the relevant two-factor
        authentication code is verified.
    :rtype: AuthenticationApi
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
