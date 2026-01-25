"""
This module provides the `Cookie` class for handling authentication cookies
related to the VRChat API. It enables operations like saving cookies to a file,
loading cookies from a file, and extracting cookies from HTTP headers.
"""


import os
import json
from typing import Dict, Optional
from dataclasses import dataclass
from http.cookies import SimpleCookie

from ..constant import constant


@dataclass(frozen=True, slots=True)
class Cookie:

    """
    Represents a Cookie containing authentication information.

    This class is used to handle operations related to cookies,
    such as saving and loading authentication data, as well as
    extracting authentication information from HTTP headers.

    :ivar auth: Authentication token stored in the cookie.
    :type auth: str
    """

    auth: str

    def save(
        self
    ) -> None:

        """
        Saves the current JSON data to a file.

        This method writes the data stored in the `self.json` attribute
        to a file specified by the constant `Constant.COOKIE`. The data
        is saved in JSON format with UTF-8 encoding and pretty-printed
        with an indentation of 2 spaces. The operation overwrites the
        file if it already exists.

        :raises FileNotFoundError: If the specified file path in
            `Constant.COOKIE` cannot be accessed.
        :raises IOError: If an I/O error occurs during the writing
            process.
        :raises TypeError: If `self.json` contains data that cannot
            be serialized into JSON.
        :return: This method does not return a value.
        :rtype: None
        """

        # Process
        with open(constant.COOKIE, "w", encoding="utf-8") as f:
            json.dump(self.json, f, ensure_ascii=False, indent=2)

    @property
    def json(
        self
    ) -> Dict[str, str]:

        """
        Provides a JSON representation of the object as a dictionary.

        The method returns a dictionary containing key-value pairs that represent
        specific attributes of the class. It is useful for serialization or sharing
        data between systems.

        :return: Dictionary representation of the object with keys as attribute
                 names and values as their corresponding data.
        :rtype: Dict[str, str]
        """

        # Process
        return {"auth": self.auth}

    @classmethod
    def load(
        cls,
        path: str = constant.COOKIE
    ) -> Optional["Cookie"]:

        """
        Loads a cookie object from the specified file path.

        This method attempts to read and deserialize a JSON file containing cookie
        information. If the file is found and successfully read, a `Cookie` object
        is created and returned. If the file does not exist or cannot be processed,
        the method will return `None`.

        :param path: The file path of the JSON file containing the cookie data.
                     Defaults to `Constant.COOKIE`.
        :type path: str
        :return: A `Cookie` object if loading is successful, otherwise `None`.
        :rtype: Optional[Cookie]
        """

        # Initialize
        cookie: Optional[Cookie]
        data:   Dict[str, str]

        # Process
        cookie = None

        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
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
        Extracts a `Cookie` object from the provided HTTP headers. If the provided
        header dictionary does not contain a "Set-Cookie" or "set-cookie" entry,
        or if the "auth" cookie value is not present, the method returns None.
        The method attempts to parse cookies from the provided header and validate
        that an "auth" cookie exists, returning it as part of a new `Cookie` object.

        :param header: The dictionary containing HTTP headers, potentially including
            cookies under the "Set-Cookie" or "set-cookie" key.
        :type header: Optional[dict]
        :return: A `Cookie` object containing the "auth" cookie value if it exists, or
            None if the "auth" cookie is not found or the provided header is invalid.
        :rtype: Optional[Cookie]
        """

        # Initialize
        set_cookie: Optional[str]
        jar:        SimpleCookie

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
