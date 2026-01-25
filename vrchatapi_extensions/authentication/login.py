"""
Provides functionality to obtain authentication required to use the VRChat API.

Primarily logs in using a cookie, so username and password are typically set to None. If there is
no cookie or login with the cookie is denied, the function uses the provided username and password
if they are not None; otherwise, it prompts for standard input.
"""


from multiprocessing import pool
from typing import Tuple, Optional

from vrchatapi_extensions.data import Cookie
from vrchatapi_extensions.utils.login_utils import (
    manual_login,
    cookie_login
)


def login(
    username: Optional[str] = None,
    password: Optional[str] = None,
    agent: Optional[str] = None
) -> Tuple[Optional[pool.ApplyResult], Optional[Cookie]]:

    """
    Authenticate a user to log in by utilizing either a saved cookie or performing
    a manual login. The function first attempts to load an existing cookie. If the
    cookie is valid, it attempts a login using the cookie. If the cookie is invalid
    or does not exist, a manual login is performed using the provided credentials
    (username, password, and agent).

    The function returns a tuple containing the result of the login process and a
    Cookie object (if successful).

    :param username: The username of the user. It can be None if relying on a saved
        cookie.
    :type username: Optional[str]
    :param password: The password of the user. It can be None if relying on a saved
        cookie.
    :type password: Optional[str]
    :param agent: The user agent string to be used for the login process. It is
        optional and can be None.
    :type agent: Optional[str]
    :return: A tuple containing the login result (`pool.ApplyResult` or None) and
        the `Cookie` object (or None) obtained after successful login.
    :rtype: Tuple[Optional[pool.ApplyResult], Optional[Cookie]]
    """

    # Initialize
    user:   Optional[pool.ApplyResult]
    cookie: Optional[Cookie]

    # Process
    cookie = Cookie.load()

    if cookie is None:
        user, cookie = manual_login(username, password, agent)
    else:
        user, cookie = cookie_login(cookie, agent)

    return user, cookie
