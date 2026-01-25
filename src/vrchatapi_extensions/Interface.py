from multiprocessing import pool
from typing import Optional

from src.vrchatapi_extensions import Cookie
from src.vrchatapi_extensions import Authentication


class Interface:
    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None
    ) -> None:

        """

        :param username:
        :param password:
        """

        # Initialize
        self.user:     Optional[pool.ApplyResult]
        self.__cookie: Optional[Cookie]

        # Process
        self.user = None
        self.__cookie = None

        self.__login(username, password)

    def __login(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None
    ) -> None:

        """

        :param username:
        :param password:
        :return:
        """

        # Process
        self.user, self.__cookie = Authentication.login(username, password)