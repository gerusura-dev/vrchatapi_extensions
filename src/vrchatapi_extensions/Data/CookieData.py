import os
import json
from typing import Dict, Optional
from dataclasses import dataclass
from http.cookies import SimpleCookie

from src.vrchatapi_extensions import Constant


@dataclass(frozen=True, slots=True)
class Cookie:
    auth: str

    def save(
        self
    ) -> None:

        """

        :return:
        """

        # Process
        with open(Constant.COOKIE, "w", encoding="utf-8") as f:
            json.dump(self.json, f, ensure_ascii=False, indent=2)

    @property
    def json(
        self
    ) -> Dict[str, str]:

        """

        :return:
        """

        # Process
        return {"auth": self.auth}

    @classmethod
    def load(
        cls,
        path: str = Constant.COOKIE
    ) -> Optional["Cookie"]:

        """

        :param path:
        :return:
        """

        # Initialize
        cookie: Optional[Cookie]
        data:   Dict[str, str]

        # Process
        cookie = None

        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
            cookie = Cookie(
                auth=data["auth"]
            )

        return cookie

    @classmethod
    def extract(
        cls,
        header: Optional[dict]
    ) -> Optional["Cookie"]:

        """

        :param header:
        :return:
        """

        # Initialize
        set_cookie: Optional[str]
        jar:        SimpleCookie
        out:        Optional[str]

        # Process
        if header is None:
            return None

        set_cookie = header.get("Set-Cookie") or header.get("set-cookie")

        if not set_cookie:
            return None

        jar = SimpleCookie(set_cookie)

        if isinstance(set_cookie, list):
            for sc in set_cookie:
                jar.load(sc)
        else:
            jar.load(str(set_cookie))

        auth = jar["auth"].value if "auth" in jar else None
        if not auth:
            return None

        return Cookie(auth=auth)
