"""
Interface class provides functionality for user authentication and management.

The class allows initialization with optional parameters such as username, password,
and agent, and provides mechanisms for logging in a user and configuring internal
user-related settings.
"""


from multiprocessing import pool
from typing import Optional

from vrchatapi_extensions import authentication
from vrchatapi_extensions.data import Cookie


class Interface:

    """
    Provides an interface for user authentication.

    This class is used to authenticate users by handling login credentials,
    session management, and the identification of user agents. It ensures
    secure access to resources by using optional username, password, and
    agent configurations.
    """

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        agent: Optional[str] = None
    ) -> None:

        """
        Initializes the class providing the setup for user authentication and relevant attributes.

        :param username: Optional; The username for login, if provided.
        :type username: Optional[str]
        :param password: Optional; The password for login, if provided.
        :type password: Optional[str]
        :param agent: Optional; The agent string used in the authentication process.
        :type agent: Optional[str]

        :raises RuntimeError: Raised if called without a valid login.
        """

        # Initialize
        self.user:     Optional[pool.ApplyResult]
        self.agent:    Optional[str]
        self.__cookie: Optional[Cookie]

        # Process
        self.user = None
        self.agent = agent
        self.__cookie = None

        self.__login(username, password, agent)

    def __login(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        agent: Optional[str] = None
    ) -> None:

        """
        Logs in a user using the provided credentials and agent.

        This method handles user authentication by sending the provided
        username, password, and agent string for verification. On successful
        login, it assigns the authenticated user details and session cookie
        to the relevant variables.

        :param username: Optional; The username or email to be used for authentication.
        :param password: Optional; The password corresponding to the username for login.
        :param agent: Optional; An identifier for the agent or application
            initiating the login process.
        :return: None
        """

        # Process
        self.user, self.__cookie = authentication.login(username, password, agent)
