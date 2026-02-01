"""

Cookieが有効化確認する機能を提供する

- verify_auth_token: VRChatAPIサーバーにCookieの有効性を問い合わせる

"""


# SECTION: Packages(Third-Party)
import vrchatapi
from vrchatapi.api.authentication_api import AuthenticationApi
from vrchatapi.api_client import ApiClient

# SECTION: Packages(Local)
from vrchatapi_extensions.constant import constant
from vrchatapi_extensions.utils import CookieVault


# SECTION: Public Functions
def verify_auth_token(
    agent: str         = constant.AGENT,
    vault: CookieVault = CookieVault()
) -> bool:

    """

    端末に保存されているCookie情報の有効性を確認するAPIエンドポイントに
    リクエストを送る機能を提供する

    :param agent:
    :type agent: str

    :param vault:
    :type vault: CookieVault

    :return: Cookieの有効性を真偽値で返す
    :rtype: bool

    """

    # Initialize
    config: vrchatapi.Configuration
    client: ApiClient
    auth:   AuthenticationApi

    # Process
    agent = agent or constant.AGENT
    config = vrchatapi.Configuration()

    if not vault.is_active:
        # NOTE: 初回のCookie読み込みを行う
        vault.load()

        if not vault.is_active:
            # NOTE: not vault.is_active => Cookieの読み込みに失敗している
            return False

    with ApiClient(config) as client:
        client.user_agent = agent
        vault.set_configuration(client)
        auth = AuthenticationApi(client)

        # INFO: auth.verify_auth_token()の戻り値は{'ok': bool値, 'token': cookie値}なので、tokenを返さないようにする
        result = auth.verify_auth_token()

    return result.ok
