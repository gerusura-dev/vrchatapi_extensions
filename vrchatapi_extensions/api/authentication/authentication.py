"""
ユーザーの認証機能に関連する機能を提供するモジュール

対象となる機能は以下の公式リファレンスにおけるAuthentication項目
https://vrchat.community/reference/
"""


# SECTION: Packages(Built-in)
from multiprocessing import pool
from typing import Optional

# SECTION: Packages(Local)
from vrchatapi_extensions.api.authentication.login import login


# SECTION: Public Classes
class Authentication:

    """
    認証に関連する機能のインターフェースを提供する

    - login -> pool.ApplyResult
    """

    @classmethod
    def login(
        cls,
        username: Optional[str] = None,
        password: Optional[str] = None,
        agent:    Optional[str] = None
    ) -> pool.ApplyResult:

        """
        VRChatのAPIサーバーに対してログインを試行する機能を提供する
        ログインは最初にCookieを用いて試行され、CookieがないまたはCookieが失効していた場合は
        username、password、2段階認証（要求された場合）を用いて
        ログインを試行する
        Cookieによるログインが失敗しない限りusernameとpasswordは利用されない
        また、usernameとpasswordがNoneの場合、標準入力からそれぞれの入力を要求する

        対象となるAPIは以下のページ
        https://vrchat.community/reference/get-current-user

        :param username: ログインを試行するユーザー名またはメールアドレス
        :type username: Optional[str]
        :param password: ログインを試行するパスワード
        :type password: Optional[str]
        :param agent: ログインリクエストに添付するエージェント
        :type agent: Optional[str]
        :return: VRChatAPIサーバーからのレスポンス
        :rtype: pool.ApplyResult
        """

        # Process
        return login(username, password, agent)
