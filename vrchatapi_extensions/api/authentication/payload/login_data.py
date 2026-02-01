"""

ログイン関係の処理に用いるデータクラスを提供する

- LoginResponse: ログインリクエストのレスポンス情報を格納する

"""


# SECTION: Packages(Built-in)
import copy
from dataclasses import dataclass
# SECTION: Packages(Type Annotation)
from multiprocessing import pool
from typing import Any, Dict


# SECTION: Public Classes
@dataclass(frozen=True, slots=True)
class LoginResponse:

    """

    ログインリクエストのレスポンスを格納するクラス

    :param __user: ログイン先のユーザー情報
    :type __user: pool.ApplyResult

    :param status: リクエストのステータスコード
    :type status: int

    :param __headers: レスポンスのヘッダー情報
    :type __headers: Dict[str, Any]

    """

    # Initialize
    __user:    pool.ApplyResult
    status:    int
    __headers: Dict[str, Any]

    @property
    def user(self) -> pool.ApplyResult:

        """

        frozen=Trueでuserへの再代入は禁止できているが
        pool.ApplyResultへの要素への再代入は禁止されていないのでプロパティを用いてコピーを返すようにし
        元のデータを保護している

        :return: サーバーから返ってきたユーザー情報
        :rtype: pool.ApplyResult

        """

        return copy.deepcopy(self.__user)

    @property
    def headers(self) -> Dict[str, Any]:

        """

        frozen=Trueでheadersへの再代入は禁止できているが
        Dict[str, Any]への要素への再代入は禁止されていないのでプロパティを用いてコピーを返すようにし
        元のデータを保護している

        :return: サーバーから返ってきたヘッダー情報
        :rtype: Dict[str, Any]

        """

        return copy.deepcopy(self.__headers)
