"""
This module handles data structures, interface definitions, and authentication
functionalities associated with the VRChat API extensions.

The module provides imports for the following components:
- `Cookie`: A module for dealing with cookie-related data structures.
- `Interface`: A module that defines interface requirements.
- `Authentication`: A module to manage authentication requests.

These imports allow for integration with the VRChat API extensions and
enhance extensibility and modularity in related applications.
"""


from vrchatapi_extensions import authentication
from vrchatapi_extensions.data import Cookie
from vrchatapi_extensions.interface import Interface


__all__ = [
    "Cookie",
    "Interface",
    "authentication"
]
