"""

ユーザーの認証機能に関連する機能を提供するモジュール

対象となる機能は以下の公式リファレンスにおけるAuthentication項目
https://vrchat.community/reference/

"""


# SECTION: Packages(Type Annotation)
from multiprocessing import pool
from typing import Optional

# SECTION: Packages(Third-Party)
from tenacity import RetryError
from vrchatapi_extensions.constant import constant
from vrchatapi_extensions.utils import CookieVault

# SECTION: Packages(Local)
from .login import login
from .payload import LoginResponse
from .verify_auth_token import verify_auth_token


# SECTION: Public Classes
class Authentication:

    """

    認証に関連する機能のインターフェースを提供する

    - login() -> LoginResponse ... GET
    - verify_auth_token() -> bool ... GET

    """

    @classmethod
    def login(
        cls,
        username: Optional[str] = None,
        password: Optional[str] = None,
        agent:    str           = constant.AGENT
    ) -> LoginResponse:

        """

        対象となるAPIは以下のページ
        https://vrchat.community/reference/get-current-user

        APIエンドポイント
        https://api.vrchat.cloud/api/1/auth/user

        login()だけ専用のpayloadはなし（username,password,agentはシンプルな引数の方が直感的）

        VRChatのAPIサーバーに対してログインを試行する機能を提供する
        ログインは最初にCookieを用いて試行され、CookieがないまたはCookieが失効していた場合は
        username、password、2段階認証（要求された場合）を用いて
        ログインを試行する
        Cookieによるログインが失敗しない限りusernameとpasswordは利用されない
        また、usernameとpasswordがNoneの場合、標準入力からそれぞれの入力を要求する
        認証は自動的に3回リトライされる

        :param username: ログインを試行するユーザー名またはメールアドレス
        :type username: Optional[str]

        :param password: ログインを試行するパスワード
        :type password: Optional[str]

        :param agent: ログインリクエストに添付するエージェント
        :type agent: str

        :return: VRChatAPIサーバーからのレスポンス
        :rtype: pool.ApplyResult

        """

        # Initialize
        result: LoginResponse

        # Process
        try:
            result = login(username, password, agent)
        except RetryError as e :
            raise e.last_attempt.result()
        except Exception as e:
            raise e

        return result

    @classmethod
    def verify_auth_token(
        cls,
        agent: Optional[str] = None,
        vault: CookieVault   = CookieVault()
    ) -> bool:

        """

        対象となるAPIは以下のページ
        https://vrchat.community/reference/verify-auth-token

        APIエンドポイント
        https://api.vrchat.cloud/api/1/auth

        端末に保存されているCookieの有効性を確認する機能を提供する

        :param agent:
        :type agent: Optional[str]

        :param vault:
        :type vault: Optional[CookieVault]

        :return: Cookieが有効であるかのbool値
        :rtype: bool

        """

        # Initialize
        result: bool

        # Process
        try:
            result = verify_auth_token(agent, vault)
        except Exception as e:
            raise e

        return result
