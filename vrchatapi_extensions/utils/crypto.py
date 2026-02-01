"""

認証に使用するCookieを管理するクラス

"""


# SECTION: Packages(Type Annotation)
from typing import (
    Any,
    Dict,
    Optional
)

# SECTION: Packages(Built-in)
import json
import os
from contextlib import suppress
from dataclasses import dataclass
from http.cookies import SimpleCookie
from pathlib import Path

# SECTION: Packages(Third-Party)
import keyring
from cryptography.fernet import Fernet
from vrchatapi import ApiClient

# SECTION: Packages(Local)
from vrchatapi_extensions.constant import constant


# SECTION: Public Classes
@dataclass(slots=True)
class CookieVault:

    """
    Manages encrypted storage and retrieval of cookies.

    This class is used to handle cookies securely by providing functionality
    to save, load, and retrieve cookies. It supports encryption and decryption
    of cookies to ensure their security. The cookies are stored in a specified
    file path, and the encryption key is securely managed using a keyring.
    """

    # Initialize
    service_name: str             = "vrchatapi_extensions"
    account_name: str             = "cookie-dek"
    store_path:   Path            = constant.COOKIE
    _ciphertext:  Optional[bytes] = None

    # SECTION: Properties
    @property
    def is_active(self) -> bool:

        """
        Checks if the current object is in an active state.

        The method evaluates whether the object holds a valid non-None
        value for its internal `_ciphertext` attribute. If `_ciphertext`
        is not None, the object is considered active.

        :return: A boolean indicating whether the object is active.
        :rtype: Bool
        """

        # Process
        return self._ciphertext is not None

    # SECTION: Public Functions
    def load(self) -> None:

        """
        Loads the ciphertext from the specified storage path if it exists.
        If the storage path does not exist, the ciphertext is set to None.

        :return: None
        """

        # Process
        if self.store_path.exists():
            self._ciphertext = self.store_path.read_bytes()
        else:
            self._ciphertext = None

    def save(
        self,
        cookies: Dict[str, str]
    ) -> None:

        """
        Saves the given cookies securely by encrypting and storing them in a specified path.
        The method ensures that the storage directory exists before writing the encrypted
        data to a file. Additionally, it attempts to set restrictive file permissions
        to enhance security post-saving.

        :param cookies: A dictionary containing the cookies to be saved as key-value pairs.
        :type cookies: Dict[str, str]
        :return: None
        """

        # Initialize
        plain: bytes
        token: bytes

        # Process
        plain = json.dumps(cookies, ensure_ascii=False).encode("utf-8")
        token = self._fernet().encrypt(plain)

        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        self.store_path.write_bytes(token)
        self._ciphertext = token

        # NOTE: Windowsではchmodがサポートされていないが、実行する必要がないのでエラーを握りつぶす
        with suppress(Exception):
            os.chmod(self.store_path, 0o600)

    def get(
        self,
        key: str
    ) -> Optional[str]:

        """
        Retrieves the value associated with the given key from a decrypted data dictionary.
        The method ensures that the returned value is a string if the key exists
        and its corresponding value is of type string. Otherwise, it returns None.

        :param key: The key whose associated value is to be retrieved. Must be a string.
        :return: The value associated with the specified key if it is of type string,
                 otherwise None.
        :rtype: Optional[str]
        """

        # Initialize
        data:  Dict[str, Any]
        value: Optional[str]

        # Process
        data = self._decrypt()
        value = data.get(key)

        return value if isinstance(value, str) else None

    def set_configuration(
        self,
        client: ApiClient
    ) -> None:

        """
        Sets the configuration for the provided client by extracting authentication
        information from the current instance and setting it in the client's default
        headers.

        :param client: The client instance whose default headers will be configured.
        :type client: Any

        :return: None
        """

        # Initialize
        auth:  Optional[str]
        twofa: Optional[str]

        header: str = ""

        # Process
        auth = self.get("auth")
        if auth is not None:
            header = f"auth={auth}"

        twofa = self.get("twoFactorAuth")
        if twofa is not None:
            header += f"; twoFactorAuth={twofa}"

        client.default_headers["Cookie"] = header

    @classmethod
    def extract(
        cls,
        header: Optional[dict]
    ) -> Optional[Dict[str, str]]:

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
        twofa = jar["twoFactorAuth"].value if "twoFactorAuth" in jar else None
        if not auth:
            return None

        return {
            "auth": auth,
            "twoFactorAuth": twofa
        }

    # SECTION: Private Functions
    def _get_key(self) -> bytes:

        """
        Generates or retrieves a cryptographic key associated with the service and
        account name from a secure keyring. If no key exists, a new cryptographic
        key is generated, stored securely, and returned.

        :return: A cryptographic key in byte format.
        :rtype: Bytes
        """

        # Initialize
        key_b64: Optional[str]
        key:     bytes

        # Process
        key_b64 = keyring.get_password(self.service_name, self.account_name)
        if key_b64 is None:
            key = Fernet.generate_key()
            keyring.set_password(self.service_name, self.account_name, key.decode("ascii"))
            return key
        return key_b64.encode("ascii")

    def _fernet(self) -> Fernet:

        """
        Generates a Fernet instance.

        This method returns an instance of the Fernet class, which is a symmetric key
        cryptography implementation. The returned instance is initialized using the
        symmetric encryption key.

        :return: Fernet instance
        :rtype: Fernet
        """

        # Process
        return Fernet(self._get_key())

    def _decrypt(self) -> Dict[str, Any]:

        """
        Decrypts the encrypted data stored in the object and returns it as a
        dictionary.

        This method uses Fernet symmetric encryption to decrypt the
        stored ciphertext. It assumes the object has valid ciphertext
        to decrypt. If the ciphertext is missing or invalid, an error
        will be raised.

        :raises RuntimeError: If the ciphertext is empty indicating the object
            has not been properly initialized with encrypted data.
        :return: A dictionary containing the decrypted data.
        :rtype: Dict[str, Any]
        """

        # Initialize
        plain: bytes

        # Process
        if not self._ciphertext:
            raise RuntimeError("cookie vault is empty. call load() or save() first.")
        plain = self._fernet().decrypt(self._ciphertext)

        return json.loads(plain.decode("utf-8"))
