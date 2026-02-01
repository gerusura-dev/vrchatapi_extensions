"""

vrchatapi_extensionsで使用する定数を定義する

Login Constant ... ログイン関係の処理で使用する定数を定義

- AGENT: ログインリクエストに添付するagentの初期値を定義
- COOKIE: 認証情報のCookieの保存先を定義
- LOGIN_RETRY_LIMIT: ログインリトライの上限回数を定義
- LOGIN_RETRY_WAIT: ログインリトライの間隔[sec]を定義

"""


# SECTION: Packages(Type Annotation)
from typing import Final

# SECTION: Packages(Built-in)
from pathlib import Path

# SECTION: Constants

## SECTION: Login Constant
AGENT:             Final[str]  = "vrchatapi-extensions/0.0.0 ext@email.com"
COOKIE:            Final[Path] = Path.home() / ".config" / "vrchatapi_extensions" / "cookie.enc"
LOGIN_RETRY_LIMIT: Final[int]  = 3
LOGIN_RETRY_WAIT:  Final[int]  = 5
