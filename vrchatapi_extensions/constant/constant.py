"""
Defines constants for use in the vrchatapi-extensions module.

These constants can be used to identify the extension agent and provide
a default path for storing the cookie used in API authentication.
"""


# SECTION: Packages(Built-in)
from pathlib import Path

# SECTION: Constants
AGENT:  str  = "vrchatapi-extensions/0.0.0 ext@email.com"
COOKIE: Path = Path.home() / ".config" / "vrchatapi_extensions" / "cookie.enc"
