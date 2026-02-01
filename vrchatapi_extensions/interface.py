"""
Interface class provides functionality for user authentication and management.

The class allows initialization with optional parameters such as username, password,
and agent, and provides mechanisms for logging in a user and configuring internal
user-related settings.
"""


# SECTION: Packages(Built-in)
from dataclasses import dataclass
from typing import Optional

# SECTION: Packages(Local)
from vrchatapi_extensions.api import Authentication


# SECTION: Public Classes
@dataclass(slots=True)
class Interface:

    """
    Provides an interface for user authentication.

    This class is used to authenticate users by handling login credentials,
    session management, and the identification of user agents. It ensures
    secure access to resources by using optional username, password, and
    agent configurations.
    """

    __cookie_verify: bool = False

    authentication = Authentication

    def __init__(self, auto_cookie_verify: bool = True) -> None:

        """
        Initializes the class providing the setup for user authentication and relevant attributes.

        :param agent: Optional; The agent string used in the authentication process.
        :type agent: Optional[str]

        :raises RuntimeError: Raised if called without a valid login.
        """

        # Process
        if auto_cookie_verify:
            self.__cookie_verify = self.authentication.verify_auth_token()

    @property
    def cookie_verify(self) -> bool:
        return self.__cookie_verify
