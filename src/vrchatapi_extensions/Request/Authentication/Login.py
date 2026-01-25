"""
vrchatapiを用いてログイン処理を行う機能を提供する
"""


from multiprocessing import pool
from typing import Tuple, Optional

from src.vrchatapi_extensions import Data
from src.vrchatapi_extensions.Utils.LoginUtils import (
    manual_login,
    cookie_login
)


def login(
    username: Optional[str] = None,
    password: Optional[str] = None
) -> Tuple[Optional[pool.ApplyResult], Optional[Data.Cookie]]:

    """
    VRChatのAPIを利用する上で必要な認証を得る機能を提供する
    基本的にはCookieを用いてログインするので、usernameとpasswordはNoneが基本となる
    CookieがないorCookieによるログインが否認された場合、
    usernameとpasswordが非Noneなら値をそのまま利用し、Noneなら標準入力を要求する

    :param username: ログインに使用するユーザー名またはメールアドレス
    :param password: ログインに使用するパスワード
    :return:Tuple[ユーザーデータ, 最新のCookie]
    """

    # Initialize
    user:   Optional[pool.ApplyResult]
    cookie: Optional[Data.Cookie]

    # Process
    cookie = Data.Cookie.load()

    if cookie is None:
        user, cookie = manual_login(username, password)
    else:
        user, cookie = cookie_login(cookie)

    return user, cookie
