"""

VRChatAPIを用いたログイン処理を行う機能を提供する
マニュアルログインとCookieログインを自動的に実行する

- login(): ログイン処理を行う

"""


# SECTION: Packages(Type Annotation)
from typing import Dict, Optional

# SECTION: Packages(Built-in)
import getpass

# SECTION: Packages(Third-Party)
import vrchatapi
from tenacity import retry, stop_after_attempt, wait_fixed
from vrchatapi.api.authentication_api import AuthenticationApi
from vrchatapi.api_client import ApiClient
from vrchatapi.exceptions import UnauthorizedException
from vrchatapi.models.two_factor_auth_code import TwoFactorAuthCode
from vrchatapi.models.two_factor_email_code import TwoFactorEmailCode

# SECTION: Packages(Local)
from vrchatapi_extensions.api.authentication.payload import LoginResponse
from vrchatapi_extensions.constant import constant
from vrchatapi_extensions.utils import CookieVault


# SECTION: Public Functions
@retry(
    stop=stop_after_attempt(constant.LOGIN_RETRY_LIMIT),
    wait=wait_fixed(constant.LOGIN_RETRY_WAIT)
)
def login(
    username: Optional[str] = None,
    password: Optional[str] = None,
    agent:    str           = constant.AGENT
) -> LoginResponse:

    """

    マニュアルログインとCookieログインを自動で実行する機能を提供する
    CookieVaultのis_active値がTrue（Cookieの読み込みに成功した）場合はCookieによるログインを試行する
    CookieVaultのis_active値がFalseの場合はマニュアルログインを試行する
    もしCookieログインに失敗した場合は自動的にマニュアルログインにフォールバックする
    ログイン試行は3回までリトライできる

    :param username: ログインに使うユーザー名またはEmailアドレス
    :type username: Optional[str]

    :param password: ログインに使うパスワード
    :type password: Optional[str]

    :param agent: ログインリクエストに添付するエージェント文字列（NoneでConstant値を利用）
    :type agent: str

    :return: LoginResultオブジェクト（APIサーバーからのレスポンス）
    :rtype: LoginResponse

    """

    # Initialize
    response: Optional[LoginResponse]
    vault:    CookieVault

    # Process
    vault = CookieVault()
    vault.load()
    if vault.is_active:
        response = __cookie_login(agent, vault)
    else:
        response = __manual_login(username, password, agent, vault)

    return response


# SECTION: Private Functions
def __manual_login(
    username: Optional[str] = None,
    password: Optional[str] = None,
    agent:    str           = constant.AGENT,
    vault:    CookieVault   = CookieVault()
) -> LoginResponse:

    """

    ユーザー名（Emailアドレス）とパスワードでログインを試行する機能を提供する

    :param username: ログインに使うユーザー名またはEmailアドレス
    :type username: Optional[str]

    :param password: ログインに使うパスワード
    :type password: Optional[str]

    :param agent: ログインリクエストに添付するエージェント文字列（NoneでConstant値を利用）
    :type agent: str

    :param vault: マニュアルログインで得たCookieを保存するためのCookieVaultオブジェクト
    :type vault: CookieVault

    :return: LoginResultオブジェクト（APIサーバーからのレスポンス）
    :rtype: LoginResponse

    """

    # Initialize
    config:   vrchatapi.Configuration
    client:   ApiClient
    auth:     AuthenticationApi
    response: LoginResponse
    cookie:   Optional[Dict[str, str]]

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
        client.user_agent = agent
        auth = AuthenticationApi(client)

        try:
            response = LoginResponse(*auth.get_current_user_with_http_info())
            cookie = vault.extract(response.headers)
            if cookie is not None:
                vault.save(cookie)
        except UnauthorizedException as e:
            auth = __two_factor_auth(auth, e.reason)
            response = LoginResponse(*auth.get_current_user_with_http_info())
            cookie = vault.extract(response.headers)
            if cookie is None:
                cookie = vault.extract(e.headers)
            vault.save(cookie)

    return response


def __cookie_login(
    agent: str         = constant.AGENT,
    vault: CookieVault = CookieVault()
) -> LoginResponse:

    """

    端末に保存されたCookieを用いてログイン処理を実行する機能を提供する
    Cookieによるログインリクエストが失敗した場合、自動的にマニュアルログインにフォールバックする

    :param agent: ログインリクエストに添付するエージェント文字列（NoneでConstant値を利用）
    :type agent: str

    :param vault: 端末に保存されたCookieの情報をマネジメントするオブジェクト
    :type vault: CookieVault

    :return: LoginResultオブジェクト（APIサーバーからのレスポンス）
    :rtype: LoginResponse

    """

    # Initialize
    config: vrchatapi.Configuration
    client: ApiClient
    auth:   AuthenticationApi
    response: LoginResponse

    # Process
    config = vrchatapi.Configuration()

    with ApiClient(config) as client:
        client.user_agent = agent
        vault.set_configuration(client)
        auth = AuthenticationApi(client)

        try:
            response = LoginResponse(*auth.get_current_user_with_http_info())
        except UnauthorizedException:
            response = __manual_login(agent=agent, vault=vault)

    return response


def __two_factor_auth(
    auth:   AuthenticationApi,
    reason: str
) -> AuthenticationApi:

    """

    マニュアルログイン時に2段階認証を要求された場合に認証を実行する機能を提供する

    :param auth: ログインリクエストを行う機能を提供するAuthenticationApiオブジェクト
    :type auth: AuthenticationApi

    :param reason: マニュアルログインが否認された理由（内容に応じて処理内容が異なる）
    :type reason: str

    :return: 2段階認証コードを設定したAuthenticationApiオブジェクト
    :type: AuthenticationApi

    """

    # Initialize
    code: str

    # Process
    if "Email 2 Factor Authentication" in reason:
        code = input("Email 2FA Code: ")
        auth.verify2_fa_email_code(two_factor_email_code=TwoFactorEmailCode(code))
    elif "2 Factor Authentication" in reason:
        code = input("2FA Code: ")
        auth.verify2_fa(two_factor_auth_code=TwoFactorAuthCode(code))

    return auth
